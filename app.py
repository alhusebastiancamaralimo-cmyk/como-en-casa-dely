import io
import re
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from supabase import create_client


# =========================================================
# 1. CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded",
)

VERSION = "4.0.0"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    :root {
        --madera: #795438;
        --madera-oscura: #4A3425;
        --madera-clara: #A9825B;
        --crema: #FAF6EE;
        --beige: #EDE0CC;
        --texto: #35271E;
    }

    .stApp {
        background: #FAF6EE;
        color: #35271E;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #4A3425;
    }

    [data-testid="stSidebar"] * {
        color: #FFF8ED !important;
    }

    h1, h2, h3 {
        color: #4A3425;
        font-family: 'Playfair Display', serif;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5D3BC;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(74, 52, 37, .06);
    }

    [data-testid="stMetricLabel"] {
        color: #795438;
    }

    .marca {
        background: linear-gradient(135deg, #4A3425, #8D6644);
        color: #FFF8ED;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 20px;
    }

    .marca h1 {
        color: #FFF8ED;
        margin-bottom: 5px;
    }

    .marca p {
        color: #F4E5D0;
        margin-bottom: 0;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"] {
        background: #795438;
        border-color: #795438;
        color: white;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #E5D3BC;
        border-radius: 15px;
        padding: 20px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E5D3BC;
        border-radius: 10px;
        overflow: hidden;
    }

    .nota {
        color: #795438;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2. CONEXIÓN A SUPABASE
# =========================================================

def obtener_secreto(nombre, predeterminado=""):
    try:
        return st.secrets.get(nombre, predeterminado)
    except Exception:
        return predeterminado


SUPABASE_URL = str(obtener_secreto("SUPABASE_URL", "")).strip()
SUPABASE_KEY = str(obtener_secreto("SUPABASE_KEY", "")).strip()
APP_PASSWORD = str(obtener_secreto("APP_PASSWORD", "")).strip()


def validar_conexion():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error(
            "Falta configurar SUPABASE_URL o SUPABASE_KEY "
            "en los secretos de Streamlit."
        )
        st.info(
            "En Streamlit Cloud, abre tu aplicación, entra en Settings "
            "y luego en Secrets."
        )
        st.stop()

    if not SUPABASE_URL.startswith("https://"):
        st.error("La URL de Supabase debe comenzar con https://.")
        st.stop()

    if ".supabase.co" not in SUPABASE_URL:
        st.error("Revisa la URL de tu proyecto de Supabase.")
        st.stop()


validar_conexion()

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as error:
    st.error(f"No se pudo iniciar la conexión: {error}")
    st.stop()


# =========================================================
# 3. FUNCIONES GENERALES
# =========================================================

def mensaje_error(error, operacion="la operación"):
    st.error(
        f"No se pudo completar {operacion}. "
        "Revisa la conexión y los permisos de Supabase."
    )
    with st.expander("Ver información técnica"):
        st.code(str(error))


def leer_tabla(tabla, columnas="*"):
    """Lee una tabla por páginas para no limitarse a 1000 filas."""
    resultados = []
    inicio = 0
    tamano = 1000

    while True:
        respuesta = (
            supabase.table(tabla)
            .select(columnas)
            .range(inicio, inicio + tamano - 1)
            .execute()
        )

        filas = respuesta.data or []
        resultados.extend(filas)

        if len(filas) < tamano:
            break

        inicio += tamano

    return resultados


def registrar_evento(operacion, detalle="", nivel="INFO"):
    try:
        supabase.table("registro_sistema").insert({
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "nivel": str(nivel)[:30],
            "operacion": str(operacion)[:100],
            "detalle": str(detalle)[:2000],
        }).execute()
    except Exception:
        # Un fallo del registro no debe bloquear un pedido.
        pass


def dinero(valor):
    try:
        return f"S/ {float(valor or 0):,.2f}"
    except (TypeError, ValueError):
        return "S/ 0.00"


def fecha_segura(valor):
    if not valor:
        return None

    try:
        return pd.to_datetime(valor, errors="coerce").date()
    except Exception:
        return None


def normalizar_nombre(valor):
    return re.sub(r"\s+", " ", str(valor or "")).strip()


def observaciones_con_direccion(direccion, observaciones):
    direccion = normalizar_nombre(direccion)
    observaciones = str(observaciones or "").strip()

    # Evita duplicar la dirección si se está editando un pedido antiguo.
    observaciones = re.sub(
        r"(?im)^\s*Dirección:\s*.*(?:\n|$)",
        "",
        observaciones,
    ).strip()

    if direccion:
        return f"Dirección: {direccion}\n{observaciones}".strip()

    return observaciones


def separar_direccion(observaciones):
    texto = str(observaciones or "")
    direccion = ""

    lineas = texto.splitlines()
    restantes = []

    for linea in lineas:
        coincidencia = re.match(
            r"^\s*Dirección:\s*(.*)$",
            linea,
            flags=re.IGNORECASE,
        )

        if coincidencia and not direccion:
            direccion = coincidencia.group(1).strip()
        else:
            restantes.append(linea)

    return direccion, "\n".join(restantes).strip()


def a_dataframe(datos):
    return pd.DataFrame(datos) if datos else pd.DataFrame()


def descargar_excel(datos, nombre_hoja="Datos"):
    """Genera un archivo Excel en memoria."""
    salida = io.BytesIO()

    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        df = pd.DataFrame(datos)

        if df.empty:
            df = pd.DataFrame({"Mensaje": ["Sin datos"]})

        df.to_excel(
            escritor,
            index=False,
            sheet_name=nombre_hoja[:31],
        )

    salida.seek(0)
    return salida.getvalue()


def exportaciones(datos, prefijo):
    df = pd.DataFrame(datos)

    if df.empty:
        st.info("No hay datos para exportar.")
        return

    izquierda, derecha = st.columns(2)

    with izquierda:
        st.download_button(
            "📄 Descargar CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{prefijo}_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with derecha:
        try:
            archivo = descargar_excel(datos, prefijo[:31])
            st.download_button(
                "📊 Descargar Excel",
                data=archivo,
                file_name=f"{prefijo}_{date.today().isoformat()}.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )
        except Exception:
            st.warning(
                "Para exportar a Excel, agrega openpyxl a requirements.txt."
            )


# =========================================================
# 4. CARGA DE DATOS
# =========================================================

@st.cache_data(ttl=20, show_spinner=False)
def cargar_pedidos():
    filas = leer_tabla("pedidos")

    for fila in filas:
        fila.setdefault("cliente", "")
        fila.setdefault("empresa", "")
        fila.setdefault("precio_menu", 0)
        fila.setdefault("cantidad_menus", 0)
        fila.setdefault("total", 0)
        fila.setdefault("observaciones", "")

    filas.sort(
        key=lambda fila: str(fila.get("fecha") or ""),
        reverse=True,
    )

    return filas


@st.cache_data(ttl=20, show_spinner=False)
def cargar_detalles():
    return leer_tabla("detalle_pedido")


@st.cache_data(ttl=30, show_spinner=False)
def cargar_empresas():
    return leer_tabla("empresas")


@st.cache_data(ttl=30, show_spinner=False)
def cargar_catalogo():
    return leer_tabla("catalogo_platos")


def refrescar_datos():
    cargar_pedidos.clear()
    cargar_detalles.clear()
    cargar_empresas.clear()
    cargar_catalogo.clear()


def detalle_de_pedido(pedido_id, todos=None):
    if todos is None:
        todos = cargar_detalles()

    return [
        detalle for detalle in todos
        if str(detalle.get("pedido_id")) == str(pedido_id)
    ]


def nombre_empresa_activa(empresa):
    nombre = normalizar_nombre(empresa)
    if not nombre:
        return ""

    return nombre


# =========================================================
# 5. ACCESO
# =========================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = not bool(APP_PASSWORD)

if APP_PASSWORD and not st.session_state.autenticado:
    st.markdown(
        """
        <div class="marca">
            <h1>🍗 Como en Casa Dely</h1>
            <p>Administración de pedidos y ventas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_acceso"):
        clave = st.text_input("Contraseña", type="password")
        entrar = st.form_submit_button(
            "Ingresar",
            type="primary",
            use_container_width=True,
        )

    if entrar:
        if clave == APP_PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("La contraseña no es correcta.")

    st.stop()


# =========================================================
# 6. ENCABEZADO Y NAVEGACIÓN
# =========================================================

with st.sidebar:
    st.markdown("## 🍗 Como en Casa Dely")
    st.caption(f"Panel administrativo · v{VERSION}")
    st.divider()

    pagina = st.radio(
        "MENÚ PRINCIPAL",
        [
            "Inicio",
            "Registrar pedido",
            "Pedidos",
            "Estadísticas",
            "Empresas",
            "Catálogo",
            "Sistema",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("🔄 Actualizar datos", use_container_width=True):
        refrescar_datos()
        st.rerun()

    if APP_PASSWORD and st.button(
        "🔒 Cerrar sesión",
        use_container_width=True,
    ):
        st.session_state.autenticado = False
        st.rerun()

st.markdown(
    """
    <div class="marca">
        <h1>Como en Casa Dely</h1>
        <p>Gestión de pedidos, empresas y ventas en un solo lugar.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 7. INICIO
# =========================================================

if pagina == "Inicio":
    st.title("Resumen del negocio")

    try:
        pedidos = cargar_pedidos()
        hoy = date.today()

        pedidos_hoy = [
            p for p in pedidos
            if fecha_segura(p.get("fecha")) == hoy
        ]

        venta_hoy = sum(
            float(p.get("total") or 0)
            for p in pedidos_hoy
        )

        menus_hoy = sum(
            int(p.get("cantidad_menus") or 0)
            for p in pedidos_hoy
        )

        empresas = cargar_empresas()
        empresas_activas = [
            e for e in empresas
            if e.get("activo", True)
        ]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Ventas de hoy", dinero(venta_hoy))
        c2.metric("Pedidos de hoy", len(pedidos_hoy))
        c3.metric("Menús vendidos hoy", menus_hoy)
        c4.metric("Empresas activas", len(empresas_activas))

        st.subheader("Pedidos recientes")

        recientes = pedidos[:10]

        if recientes:
            filas = []

            for p in recientes:
                direccion, notas = separar_direccion(
                    p.get("observaciones", "")
                )

                filas.append({
                    "Fecha": p.get("fecha", ""),
                    "Cliente": p.get("cliente", ""),
                    "Empresa": p.get("empresa", ""),
                    "Menús": p.get("cantidad_menus", 0),
                    "Total": dinero(p.get("total", 0)),
                })

            st.dataframe(
                pd.DataFrame(filas),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Todavía no hay pedidos registrados.")

        st.subheader("Accesos rápidos")
        a, b, c = st.columns(3)

        with a:
            if st.button("➕ Registrar pedido", use_container_width=True):
                st.session_state.pagina_rapida = "Registrar pedido"
                st.rerun()

        with b:
            if st.button("🏢 Gestionar empresas", use_container_width=True):
                st.session_state.pagina_rapida = "Empresas"
                st.rerun()

        with c:
            if st.button("📊 Ver estadísticas", use_container_width=True):
                st.session_state.pagina_rapida = "Estadísticas"
                st.rerun()

    except Exception as error:
        mensaje_error(error, "cargar el resumen")


# =========================================================
# 8. REGISTRAR PEDIDO
# =========================================================

elif pagina == "Registrar pedido":
    st.title("➕ Registrar un pedido")
    st.write("Completa los datos del cliente y los menús solicitados.")

    # Los campos se limpian antes de volver a crear los widgets.
    if st.session_state.pop("limpiar_form_pedido", False):
        for clave in [
            "rp_cliente", "rp_empresa", "rp_direccion",
            "rp_fecha", "rp_precio", "rp_cantidad",
            "rp_entrada", "rp_segundo", "rp_bebida",
            "rp_obs", "rp_cantidad_entrada",
            "rp_cantidad_segundo", "rp_cantidad_bebida",
        ]:
            st.session_state.pop(clave, None)

    try:
        empresas = [
            e for e in cargar_empresas()
            if e.get("activo", True)
        ]

        nombres_empresas = sorted({
            normalizar_nombre(e.get("nombre"))
            for e in empresas
            if normalizar_nombre(e.get("nombre"))
        })

        opciones_empresa = ["Sin empresa"] + nombres_empresas

        with st.form("form_registrar_pedido"):
            st.subheader("Datos del pedido")

            col1, col2 = st.columns(2)

            with col1:
                cliente = st.text_input(
                    "Nombre del cliente *",
                    key="rp_cliente",
                    placeholder="Ej. Juan Pérez",
                )

                empresa = st.selectbox(
                    "Empresa",
                    opciones_empresa,
                    key="rp_empresa",
                )

                direccion = st.text_input(
                    "Dirección de entrega",
                    key="rp_direccion",
                    placeholder="Calle, número, distrito...",
                )

                fecha_pedido = st.date_input(
                    "Fecha del pedido",
                    value=date.today(),
                    key="rp_fecha",
                )

            with col2:
                precio_menu = st.number_input(
                    "Precio por menú (S/)",
                    min_value=0.0,
                    value=15.0,
                    step=0.5,
                    format="%.2f",
                    key="rp_precio",
                )

                cantidad_menus = st.number_input(
                    "Cantidad de menús",
                    min_value=1,
                    max_value=10000,
                    value=1,
                    step=1,
                    key="rp_cantidad",
                )

                st.markdown("**Detalle de los platos**")

                entrada = st.text_input(
                    "Entrada",
                    key="rp_entrada",
                    placeholder="Ej. Papa a la huancaína",
                )

                cantidad_entrada = st.number_input(
                    "Cantidad de entradas",
                    min_value=0,
                    max_value=10000,
                    value=1,
                    step=1,
                    key="rp_cantidad_entrada",
                )

                segundo = st.text_input(
                    "Segundo",
                    key="rp_segundo",
                    placeholder="Ej. Pollo broaster",
                )

                cantidad_segundo = st.number_input(
                    "Cantidad de segundos",
                    min_value=0,
                    max_value=10000,
                    value=1,
                    step=1,
                    key="rp_cantidad_segundo",
                )

                bebida = st.text_input(
                    "Bebida u otro adicional",
                    key="rp_bebida",
                    placeholder="Opcional",
                )

                cantidad_bebida = st.number_input(
                    "Cantidad de bebidas/adicionales",
                    min_value=0,
                    max_value=10000,
                    value=0,
                    step=1,
                    key="rp_cantidad_bebida",
                )

            observaciones = st.text_area(
                "Observaciones",
                key="rp_obs",
                placeholder="Indicaciones, cambios, detalles...",
            )

            total_estimado = float(precio_menu) * int(cantidad_menus)

            st.info(
                f"Total calculado: **{dinero(total_estimado)}** "
                f"({int(cantidad_menus)} × {dinero(precio_menu)})"
            )

            guardar = st.form_submit_button(
                "💾 Guardar pedido",
                type="primary",
                use_container_width=True,
            )

        if guardar:
            cliente_limpio = normalizar_nombre(cliente)
            empresa_limpia = (
                "" if empresa == "Sin empresa"
                else normalizar_nombre(empresa)
            )

            if not cliente_limpio:
                st.error("Escribe el nombre del cliente.")
            elif precio_menu <= 0:
                st.error("El precio del menú debe ser mayor que cero.")
            elif cantidad_menus < 1:
                st.error("La cantidad de menús debe ser al menos 1.")
            else:
                total = round(
                    float(precio_menu) * int(cantidad_menus),
                    2,
                )

                obs_finales = observaciones_con_direccion(
                    direccion,
                    observaciones,
                )

                datos_pedido = {
                    "fecha": fecha_pedido.isoformat(),
                    "cliente": cliente_limpio,
                    "empresa": empresa_limpia,
                    "precio_menu": float(precio_menu),
                    "cantidad_menus": int(cantidad_menus),
                    "total": total,
                    "observaciones": obs_finales,
                }

                detalles = []

                if normalizar_nombre(entrada) and int(cantidad_entrada) > 0:
                    detalles.append({
                        "tipo": "Entrada",
                        "plato": normalizar_nombre(entrada),
                        "cantidad": int(cantidad_entrada),
                    })

                if normalizar_nombre(segundo) and int(cantidad_segundo) > 0:
                    detalles.append({
                        "tipo": "Segundo",
                        "plato": normalizar_nombre(segundo),
                        "cantidad": int(cantidad_segundo),
                    })

                if normalizar_nombre(bebida) and int(cantidad_bebida) > 0:
                    detalles.append({
                        "tipo": "Bebida/Adicional",
                        "plato": normalizar_nombre(bebida),
                        "cantidad": int(cantidad_bebida),
                    })

                pedido_id = None

                try:
                    respuesta = (
                        supabase.table("pedidos")
                        .insert(datos_pedido)
                        .execute()
                    )

                    if not respuesta.data:
                        raise RuntimeError(
                            "Supabase no devolvió el pedido creado."
                        )

                    pedido_id = respuesta.data[0].get("id")

                    if pedido_id is None:
                        raise RuntimeError(
                            "No se recibió el identificador del pedido."
                        )

                    if detalles:
                        filas_detalle = [
                            {
                                "pedido_id": pedido_id,
                                **detalle,
                            }
                            for detalle in detalles
                        ]

                        try:
                            supabase.table("detalle_pedido").insert(
                                filas_detalle
                            ).execute()
                        except Exception:
                            # Evita dejar un pedido incompleto si fallan
                            # los detalles al registrar uno nuevo.
                            try:
                                supabase.table("pedidos").delete().eq(
                                    "id", pedido_id
                                ).execute()
                            except Exception:
                                pass

                            raise RuntimeError(
                                "No se guardaron los platos. "
                                "Se intentó cancelar el pedido para evitar "
                                "un registro incompleto."
                            )

                    registrar_evento(
                        "CREAR_PEDIDO",
                        f"Pedido {pedido_id}; cliente={cliente_limpio}; "
                        f"total={total}",
                    )

                    refrescar_datos()
                    st.session_state.limpiar_form_pedido = True
                    st.success(
                        f"Pedido #{pedido_id} guardado correctamente. "
                        f"Total: {dinero(total)}"
                    )
                    st.rerun()

                except Exception as error:
                    mensaje_error(error, "guardar el pedido")

    except Exception as error:
        mensaje_error(error, "cargar los datos para el registro")


# =========================================================
# 9. HISTORIAL, EDICIÓN Y ELIMINACIÓN DE PEDIDOS
# =========================================================

elif pagina == "Pedidos":
    st.title("📋 Historial de pedidos")

    try:
        pedidos = cargar_pedidos()

        if not pedidos:
            st.info("Todavía no hay pedidos.")
        else:
            busqueda = st.text_input(
                "Buscar por cliente, empresa o número de pedido",
                placeholder="Escribe para buscar...",
            )

            c1, c2 = st.columns(2)

            with c1:
                desde = st.date_input(
                    "Desde",
                    value=date.today() - timedelta(days=30),
                    key="hist_desde",
                )

            with c2:
                hasta = st.date_input(
                    "Hasta",
                    value=date.today(),
                    key="hist_hasta",
                )

            if desde > hasta:
                st.error("La fecha inicial no puede ser posterior a la final.")
                st.stop()

            filtrados = []

            for pedido in pedidos:
                fecha_pedido = fecha_segura(pedido.get("fecha"))

                if fecha_pedido and not (desde <= fecha_pedido <= hasta):
                    continue

                texto_busqueda = " ".join([
                    str(pedido.get("id", "")),
                    str(pedido.get("cliente", "")),
                    str(pedido.get("empresa", "")),
                ]).lower()

                if busqueda.strip() and busqueda.lower() not in texto_busqueda:
                    continue

                filtrados.append(pedido)

            tabla = []

            for p in filtrados:
                direccion, notas = separar_direccion(
                    p.get("observaciones", "")
                )

                tabla.append({
                    "ID": p.get("id"),
                    "Fecha": p.get("fecha", ""),
                    "Cliente": p.get("cliente", ""),
                    "Empresa": p.get("empresa", ""),
                    "Precio": dinero(p.get("precio_menu", 0)),
                    "Menús": p.get("cantidad_menus", 0),
                    "Total": dinero(p.get("total", 0)),
                    "Dirección": direccion,
                    "Observaciones": notas,
                })

            st.dataframe(
                pd.DataFrame(tabla),
                use_container_width=True,
                hide_index=True,
            )

            st.caption(f"Pedidos encontrados: {len(filtrados)}")

            exportaciones(tabla, "pedidos")

            st.divider()
            st.subheader("Editar o eliminar un pedido")

            ids = [p.get("id") for p in filtrados if p.get("id") is not None]

            if ids:
                pedido_id = st.selectbox(
                    "Selecciona el pedido",
                    ids,
                    format_func=lambda x: (
                        f"Pedido #{x} — "
                        + str(next(
                            (
                                p.get("cliente", "")
                                for p in filtrados
                                if str(p.get("id")) == str(x)
                            ),
                            "",
                        ))
                    ),
                )

                pedido = next(
                    p for p in filtrados
                    if str(p.get("id")) == str(pedido_id)
                )

                direccion_actual, notas_actuales = separar_direccion(
                    pedido.get("observaciones", "")
                )

                with st.expander("✏️ Editar datos del pedido"):
                    with st.form("form_editar_pedido"):
                        nuevo_cliente = st.text_input(
                            "Cliente",
                            value=str(pedido.get("cliente", "")),
                        )

                        nueva_empresa = st.text_input(
                            "Empresa",
                            value=str(pedido.get("empresa", "")),
                        )

                        nueva_direccion = st.text_input(
                            "Dirección",
                            value=direccion_actual,
                        )

                        fecha_actual = (
                            fecha_segura(pedido.get("fecha")) or date.today()
                        )

                        nueva_fecha = st.date_input(
                            "Fecha",
                            value=fecha_actual,
                        )

                        nuevo_precio = st.number_input(
                            "Precio por menú",
                            min_value=0.0,
                            value=float(pedido.get("precio_menu") or 0),
                            step=0.5,
                        )

                        nueva_cantidad = st.number_input(
                            "Cantidad de menús",
                            min_value=1,
                            max_value=10000,
                            value=max(
                                1,
                                int(pedido.get("cantidad_menus") or 1),
                            ),
                            step=1,
                        )

                        nuevas_notas = st.text_area(
                            "Observaciones",
                            value=notas_actuales,
                        )

                        st.caption(
                            "La edición conserva los platos del pedido. "
                            "Los datos del cliente, fecha y total sí se actualizan."
                        )

                        guardar_edicion = st.form_submit_button(
                            "Guardar cambios",
                            type="primary",
                            use_container_width=True,
                        )

                    if guardar_edicion:
                        if not normalizar_nombre(nuevo_cliente):
                            st.error("El cliente no puede quedar vacío.")
                        elif nuevo_precio <= 0:
                            st.error("El precio debe ser mayor que cero.")
                        else:
                            try:
                                nuevo_total = round(
                                    float(nuevo_precio) * int(nueva_cantidad),
                                    2,
                                )

                                nuevo_registro = {
                                    "fecha": nueva_fecha.isoformat(),
                                    "cliente": normalizar_nombre(nuevo_cliente),
                                    "empresa": normalizar_nombre(nueva_empresa),
                                    "precio_menu": float(nuevo_precio),
                                    "cantidad_menus": int(nueva_cantidad),
                                    "total": nuevo_total,
                                    "observaciones": (
                                        observaciones_con_direccion(
                                            nueva_direccion,
                                            nuevas_notas,
                                        )
                                    ),
                                }

                                supabase.table("pedidos").update(
                                    nuevo_registro
                                ).eq("id", pedido_id).execute()

                                registrar_evento(
                                    "EDITAR_PEDIDO",
                                    f"Pedido {pedido_id}; "
                                    f"cliente={nuevo_cliente}",
                                )

                                refrescar_datos()
                                st.success("Pedido actualizado.")
                                st.rerun()

                            except Exception as error:
                                mensaje_error(error, "actualizar el pedido")

                with st.expander("🗑️ Eliminar un pedido"):
                    st.warning(
                        "Esta acción elimina el pedido y sus platos asociados. "
                        "No se puede deshacer."
                    )

                    confirmar = st.checkbox(
                        f"Confirmo que quiero eliminar el pedido #{pedido_id}",
                        key=f"confirmar_eliminar_{pedido_id}",
                    )

                    if st.button(
                        "Eliminar pedido seleccionado",
                        type="primary",
                        disabled=not confirmar,
                    ):
                        try:
                            # Primero se eliminan los detalles asociados.
                            supabase.table("detalle_pedido").delete().eq(
                                "pedido_id", pedido_id
                            ).execute()

                            supabase.table("pedidos").delete().eq(
                                "id", pedido_id
                            ).execute()

                            registrar_evento(
                                "ELIMINAR_PEDIDO",
                                f"Pedido {pedido_id}",
                                "AVISO",
                            )

                            refrescar_datos()
                            st.success("Pedido eliminado.")
                            st.rerun()

                        except Exception as error:
                            mensaje_error(error, "eliminar el pedido")

    except Exception as error:
        mensaje_error(error, "cargar el historial")


# =========================================================
# 10. ESTADÍSTICAS
# =========================================================

elif pagina == "Estadísticas":
    st.title("📊 Estadísticas de ventas")

    try:
        pedidos = cargar_pedidos()

        if not pedidos:
            st.info("Registra pedidos para comenzar a ver estadísticas.")
        else:
            fechas_validas = [
                fecha_segura(p.get("fecha"))
                for p in pedidos
                if fecha_segura(p.get("fecha")) is not None
            ]

            fecha_minima = min(fechas_validas) if fechas_validas else date.today()
            fecha_maxima = max(fechas_validas) if fechas_validas else date.today()

            c1, c2 = st.columns(2)

            with c1:
                inicio = st.date_input(
                    "Fecha inicial",
                    value=max(fecha_minima, date.today() - timedelta(days=30)),
                    min_value=fecha_minima,
                    max_value=fecha_maxima,
                    key="estad_desde",
                )

            with c2:
                fin = st.date_input(
                    "Fecha final",
                    value=fecha_maxima,
                    min_value=fecha_minima,
                    max_value=fecha_maxima,
                    key="estad_hasta",
                )

            if inicio > fin:
                st.error("La fecha inicial debe ser anterior a la final.")
                st.stop()

            seleccionados = [
                p for p in pedidos
                if fecha_segura(p.get("fecha")) is not None
                and inicio <= fecha_segura(p.get("fecha")) <= fin
            ]

            ventas = sum(float(p.get("total") or 0) for p in seleccionados)
            cantidad = sum(
                int(p.get("cantidad_menus") or 0)
                for p in seleccionados
            )

            a, b, c = st.columns(3)
            a.metric("Ventas del período", dinero(ventas))
            b.metric("Pedidos", len(seleccionados))
            c.metric("Menús vendidos", cantidad)

            st.subheader("Ventas por empresa")

            resumen_empresa = {}

            for p in seleccionados:
                empresa = normalizar_nombre(p.get("empresa")) or "Sin empresa"
                resumen_empresa.setdefault(
                    empresa,
                    {"Pedidos": 0, "Menús": 0, "Ventas": 0.0},
                )

                resumen_empresa[empresa]["Pedidos"] += 1
                resumen_empresa[empresa]["Menús"] += int(
                    p.get("cantidad_menus") or 0
                )
                resumen_empresa[empresa]["Ventas"] += float(
                    p.get("total") or 0
                )

            datos_empresa = []

            for empresa, valores in sorted(
                resumen_empresa.items(),
                key=lambda elemento: elemento[1]["Ventas"],
                reverse=True,
            ):
                datos_empresa.append({
                    "Empresa": empresa,
                    "Pedidos": valores["Pedidos"],
                    "Menús": valores["Menús"],
                    "Ventas": round(valores["Ventas"], 2),
                })

            if datos_empresa:
                df_empresas = pd.DataFrame(datos_empresa)

                st.dataframe(
                    df_empresas,
                    use_container_width=True,
                    hide_index=True,
                )

                st.bar_chart(
                    df_empresas.set_index("Empresa")["Ventas"]
                )

            st.subheader("Ventas por día")

            ventas_dia = {}

            for p in seleccionados:
                f = fecha_segura(p.get("fecha"))
                if f:
                    clave = f.isoformat()
                    ventas_dia[clave] = (
                        ventas_dia.get(clave, 0)
                        + float(p.get("total") or 0)
                    )

            if ventas_dia:
                df_dias = pd.DataFrame(
                    [
                        {"Fecha": f, "Ventas": v}
                        for f, v in sorted(ventas_dia.items())
                    ]
                )

                st.line_chart(
                    df_dias.set_index("Fecha")["Ventas"]
                )

            exportaciones(seleccionados, "estadisticas_pedidos")

    except Exception as error:
        mensaje_error(error, "calcular las estadísticas")


# =========================================================
# 11. EMPRESAS INDEPENDIENTES
# =========================================================

elif pagina == "Empresas":
    st.title("🏢 Gestión de empresas")
    st.write(
        "Las empresas se guardan de forma independiente a los pedidos. "
        "Puedes registrarlas antes de recibir una orden."
    )

    try:
        empresas = cargar_empresas()

        with st.expander("➕ Registrar una empresa", expanded=not bool(empresas)):
            with st.form("form_nueva_empresa"):
                nombre = st.text_input(
                    "Nombre de la empresa *",
                    placeholder="Nombre comercial",
                )

                contacto = st.text_input("Persona de contacto")
                telefono = st.text_input("Teléfono")
                direccion = st.text_input("Dirección")
                observaciones = st.text_area("Observaciones")

                crear = st.form_submit_button(
                    "Guardar empresa",
                    type="primary",
                    use_container_width=True,
                )

            if crear:
                nombre_limpio = normalizar_nombre(nombre)

                if not nombre_limpio:
                    st.error("Escribe el nombre de la empresa.")
                else:
                    duplicada = any(
                        normalizar_nombre(e.get("nombre")).casefold()
                        == nombre_limpio.casefold()
                        for e in empresas
                    )

                    if duplicada:
                        st.error("Ya existe una empresa con ese nombre.")
                    else:
                        try:
                            supabase.table("empresas").insert({
                                "nombre": nombre_limpio,
                                "contacto": normalizar_nombre(contacto),
                                "telefono": normalizar_nombre(telefono),
                                "direccion": normalizar_nombre(direccion),
                                "observaciones": observaciones.strip(),
                                "activo": True,
                            }).execute()

                            registrar_evento(
                                "CREAR_EMPRESA",
                                nombre_limpio,
                            )

                            refrescar_datos()
                            st.success("Empresa registrada correctamente.")
                            st.rerun()

                        except Exception as error:
                            mensaje_error(error, "registrar la empresa")

        st.subheader("Empresas registradas")

        empresas = cargar_empresas()

        if empresas:
            mostrar = []

            for e in empresas:
                mostrar.append({
                    "ID": e.get("id"),
                    "Empresa": e.get("nombre", ""),
                    "Contacto": e.get("contacto", ""),
                    "Teléfono": e.get("telefono", ""),
                    "Dirección": e.get("direccion", ""),
                    "Estado": (
                        "Activa" if e.get("activo", True) else "Inactiva"
                    ),
                    "Observaciones": e.get("observaciones", ""),
                })

            st.dataframe(
                pd.DataFrame(mostrar),
                use_container_width=True,
                hide_index=True,
            )

            exportaciones(mostrar, "empresas")

            ids_empresas = [
                e.get("id") for e in empresas
                if e.get("id") is not None
            ]

            st.divider()
            st.subheader("Editar o cambiar estado")

            empresa_id = st.selectbox(
                "Selecciona una empresa",
                ids_empresas,
                format_func=lambda x: (
                    f"#{x} — "
                    + str(next(
                        (
                            e.get("nombre", "")
                            for e in empresas
                            if str(e.get("id")) == str(x)
                        ),
                        "",
                    ))
                ),
            )

            empresa_actual = next(
                e for e in empresas
                if str(e.get("id")) == str(empresa_id)
            )

            with st.form("form_editar_empresa"):
                nombre_editado = st.text_input(
                    "Nombre",
                    value=str(empresa_actual.get("nombre", "")),
                )

                contacto_editado = st.text_input(
                    "Contacto",
                    value=str(empresa_actual.get("contacto", "")),
                )

                telefono_editado = st.text_input(
                    "Teléfono",
                    value=str(empresa_actual.get("telefono", "")),
                )

                direccion_editada = st.text_input(
                    "Dirección",
                    value=str(empresa_actual.get("direccion", "")),
                )

                observaciones_editadas = st.text_area(
                    "Observaciones",
                    value=str(empresa_actual.get("observaciones", "")),
                )

                activo_editado = st.checkbox(
                    "Empresa activa",
                    value=bool(empresa_actual.get("activo", True)),
                )

                actualizar_empresa = st.form_submit_button(
                    "Guardar cambios de empresa",
                    type="primary",
                    use_container_width=True,
                )

            if actualizar_empresa:
                nombre_nuevo = normalizar_nombre(nombre_editado)

                if not nombre_nuevo:
                    st.error("El nombre no puede quedar vacío.")
                else:
                    existe = any(
                        str(e.get("id")) != str(empresa_id)
                        and normalizar_nombre(e.get("nombre")).casefold()
                        == nombre_nuevo.casefold()
                        for e in empresas
                    )

                    if existe:
                        st.error("Otra empresa ya utiliza ese nombre.")
                    else:
                        try:
                            nombre_anterior = normalizar_nombre(
                                empresa_actual.get("nombre")
                            )

                            supabase.table("empresas").update({
                                "nombre": nombre_nuevo,
                                "contacto": normalizar_nombre(contacto_editado),
                                "telefono": normalizar_nombre(telefono_editado),
                                "direccion": normalizar_nombre(direccion_editada),
                                "observaciones": observaciones_editadas.strip(),
                                "activo": bool(activo_editado),
                            }).eq("id", empresa_id).execute()

                            # Actualiza la referencia en pedidos antiguos
                            # cuando solo se cambió el nombre.
                            if nombre_anterior != nombre_nuevo:
                                supabase.table("pedidos").update({
                                    "empresa": nombre_nuevo
                                }).eq("empresa", nombre_anterior).execute()

                            registrar_evento(
                                "EDITAR_EMPRESA",
                                f"Empresa {empresa_id}: {nombre_nuevo}",
                            )

                            refrescar_datos()
                            st.success("Empresa actualizada.")
                            st.rerun()

                        except Exception as error:
                            mensaje_error(error, "actualizar la empresa")

        else:
            st.info("Aún no hay empresas registradas.")

    except Exception as error:
        mensaje_error(error, "gestionar las empresas")


# =========================================================
# 12. CATÁLOGO
# =========================================================

elif pagina == "Catálogo":
    st.title("🍽️ Catálogo de platos")
    st.write(
        "Administra las entradas, segundos, bebidas y otros productos "
        "que utilizas habitualmente."
    )

    try:
        catalogo = cargar_catalogo()

        with st.expander("➕ Agregar plato", expanded=not bool(catalogo)):
            with st.form("form_nuevo_plato"):
                nombre_plato = st.text_input("Nombre del plato *")

                tipo_plato = st.selectbox(
                    "Tipo",
                    [
                        "Entrada",
                        "Segundo",
                        "Bebida",
                        "Extra",
                        "Otro",
                    ],
                )

                agregar_plato = st.form_submit_button(
                    "Guardar plato",
                    type="primary",
                    use_container_width=True,
                )

            if agregar_plato:
                nombre_limpio = normalizar_nombre(nombre_plato)

                if not nombre_limpio:
                    st.error("Escribe el nombre del plato.")
                else:
                    existe = any(
                        normalizar_nombre(p.get("nombre")).casefold()
                        == nombre_limpio.casefold()
                        and str(p.get("tipo", "")).casefold()
                        == tipo_plato.casefold()
                        for p in catalogo
                    )

                    if existe:
                        st.error("Ese plato ya existe en ese tipo.")
                    else:
                        try:
                            supabase.table("catalogo_platos").insert({
                                "tipo": tipo_plato,
                                "nombre": nombre_limpio,
                                "activo": True,
                            }).execute()

                            registrar_evento(
                                "CREAR_PLATO",
                                f"{tipo_plato}: {nombre_limpio}",
                            )

                            refrescar_datos()
                            st.success("Plato agregado al catálogo.")
                            st.rerun()

                        except Exception as error:
                            mensaje_error(error, "agregar el plato")

        catalogo = cargar_catalogo()

        if catalogo:
            mostrar_catalogo = [
                {
                    "ID": p.get("id"),
                    "Tipo": p.get("tipo", ""),
                    "Plato": p.get("nombre", ""),
                    "Estado": (
                        "Activo" if p.get("activo", True) else "Inactivo"
                    ),
                }
                for p in catalogo
            ]

            st.dataframe(
                pd.DataFrame(mostrar_catalogo),
                use_container_width=True,
                hide_index=True,
            )

            ids_platos = [
                p.get("id") for p in catalogo
                if p.get("id") is not None
            ]

            st.subheader("Editar un plato")

            plato_id = st.selectbox(
                "Selecciona un plato",
                ids_platos,
                format_func=lambda x: (
                    f"#{x} — "
                    + str(next(
                        (
                            p.get("nombre", "")
                            for p in catalogo
                            if str(p.get("id")) == str(x)
                        ),
                        "",
                    ))
                ),
            )

            plato_actual = next(
                p for p in catalogo
                if str(p.get("id")) == str(plato_id)
            )

            with st.form("form_editar_plato"):
                plato_nombre_editado = st.text_input(
                    "Nombre",
                    value=str(plato_actual.get("nombre", "")),
                )

                tipos = [
                    "Entrada", "Segundo", "Bebida", "Extra", "Otro"
                ]

                tipo_actual = str(plato_actual.get("tipo", "Otro"))
                if tipo_actual not in tipos:
                    tipos.append(tipo_actual)

                plato_tipo_editado = st.selectbox(
                    "Tipo",
                    tipos,
                    index=tipos.index(tipo_actual),
                )

                plato_activo_editado = st.checkbox(
                    "Plato activo",
                    value=bool(plato_actual.get("activo", True)),
                )

                guardar_plato = st.form_submit_button(
                    "Guardar cambios",
                    type="primary",
                    use_container_width=True,
                )

            if guardar_plato:
                nombre_nuevo = normalizar_nombre(plato_nombre_editado)

                if not nombre_nuevo:
                    st.error("El nombre no puede quedar vacío.")
                else:
                    try:
                        supabase.table("catalogo_platos").update({
                            "nombre": nombre_nuevo,
                            "tipo": plato_tipo_editado,
                            "activo": bool(plato_activo_editado),
                        }).eq("id", plato_id).execute()

                        registrar_evento(
                            "EDITAR_PLATO",
                            f"Plato {plato_id}: {nombre_nuevo}",
                        )

                        refrescar_datos()
                        st.success("Plato actualizado.")
                        st.rerun()

                    except Exception as error:
                        mensaje_error(error, "actualizar el plato")

        else:
            st.info("El catálogo está vacío. Puedes agregar tu primer plato.")

    except Exception as error:
        mensaje_error(error, "gestionar el catálogo")


# =========================================================
# 13. REGISTRO DEL SISTEMA
# =========================================================

elif pagina == "Sistema":
    st.title("⚙️ Sistema")
    st.write("Información de actividad y estado de la aplicación.")

    st.metric("Versión de la aplicación", VERSION)

    if st.button("Comprobar conexión con Supabase"):
        try:
            supabase.table("pedidos").select("id").limit(1).execute()
            st.success("Conexión con Supabase correcta.")
        except Exception as error:
            mensaje_error(error, "comprobar la conexión")

    st.subheader("Actividad reciente")

    try:
        eventos = leer_tabla("registro_sistema")

        eventos.sort(
            key=lambda e: str(e.get("fecha") or ""),
            reverse=True,
        )

        if eventos:
            st.dataframe(
                pd.DataFrame(eventos[:200]),
                use_container_width=True,
                hide_index=True,
            )
            exportaciones(eventos[:200], "registro_sistema")
        else:
            st.info("Todavía no hay eventos registrados.")

    except Exception as error:
        mensaje_error(error, "leer el registro del sistema")


# =========================================================
# 14. PIE DE PÁGINA
# =========================================================

st.divider()

st.caption(
    f"Como en Casa Dely · Sistema de pedidos y ventas · Versión {VERSION}"
)
