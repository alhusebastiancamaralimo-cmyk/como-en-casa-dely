import os
import re
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

import pandas as pd
import streamlit as st
from supabase import create_client


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NOMBRE_APP = "Como en Casa Dely"
VERSION_APP = "2.0.0"
PRECIO_MINIMO = 10.0
PRECIO_MAXIMO = 20.0
TAMANO_PAGINA = 1000

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    .stApp {
        background: #FAF7F0;
        color: #34271F;
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #30231D;
    }

    [data-testid="stSidebar"] * {
        color: #FFF9F0;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: 100%;
        text-align: left;
        border: 1px solid #61483A;
        background: #3D2D24;
        color: #FFF9F0;
        border-radius: 12px;
        min-height: 44px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: #8D382A;
        border-color: #C77A57;
    }

    h1, h2, h3 {
        color: #5D2F24;
        font-family: 'Playfair Display', serif;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E9DFD1;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 3px 12px rgba(65, 42, 27, .04);
    }

    [data-testid="stMetricLabel"] {
        color: #776354;
    }

    [data-testid="stMetricValue"] {
        color: #8D382A;
        font-weight: 700;
    }

    div[data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E9DFD1;
        padding: 20px;
        border-radius: 16px;
    }

    .marca {
        background: linear-gradient(135deg, #4A2D23, #8D382A);
        color: #FFF9F0;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 20px;
    }

    .marca h1 {
        color: #FFF9F0;
        margin: 0;
        font-size: 30px;
    }

    .marca p {
        color: #F4DFCA;
        margin: 7px 0 0 0;
    }

    .nota {
        background: #F1E6D8;
        border-left: 4px solid #A34B35;
        padding: 12px 16px;
        border-radius: 8px;
        color: #4A3428;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button {
        background: #8D382A;
        border-color: #8D382A;
        color: white;
        border-radius: 10px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button:hover {
        background: #6F2B21;
        border-color: #6F2B21;
        color: white;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E9DFD1;
        border-radius: 12px;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 2. FUNCIONES GENERALES
# ============================================================

def hoy_peru():
    """Fecha local de Perú."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Lima")).date()
    except Exception:
        return date.today()


def dinero(valor):
    try:
        return f"S/ {float(valor or 0):,.2f}"
    except (ValueError, TypeError):
        return "S/ 0.00"


def limpiar_texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


def convertir_numero(valor, predeterminado=0.0):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return predeterminado


def mostrar_marca():
    st.markdown(
        f"""
        <div class="marca">
            <h1>🍽️ {NOMBRE_APP}</h1>
            <p>Control de pedidos, menús, ventas y empresas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_error(mensaje, error=None):
    st.error(mensaje)
    if error is not None:
        with st.expander("Ver detalles técnicos"):
            st.code(str(error))


def registrar_evento(nivel, operacion, detalle=""):
    """El registro de eventos nunca debe tumbar la aplicación."""
    try:
        supabase.table("registro_sistema").insert({
            "nivel": str(nivel)[:30],
            "operacion": str(operacion)[:150],
            "detalle": str(detalle)[:4000],
        }).execute()
    except Exception:
        pass


def normalizar_platos(lista):
    """Limpia duplicados y valores vacíos conservando el orden."""
    resultado = []
    vistos = set()

    for plato in lista or []:
        nombre = limpiar_texto(plato)
        clave = nombre.casefold()

        if nombre and clave not in vistos:
            resultado.append(nombre)
            vistos.add(clave)

    return resultado


def separar_platos(texto):
    """Permite ingresar platos separados por comas o saltos de línea."""
    if not texto:
        return []

    partes = re.split(r"[,;\n]+", str(texto))
    return normalizar_platos(partes)


def leer_tabla(nombre_tabla, orden=None, descendente=False):
    """
    Lee registros por páginas para evitar quedarse solo con
    los primeros resultados que devuelve Supabase.
    """
    registros = []
    inicio = 0

    while True:
        consulta = supabase.table(nombre_tabla).select("*")

        if orden:
            consulta = consulta.order(orden, desc=descendente)

        respuesta = consulta.range(
            inicio, inicio + TAMANO_PAGINA - 1
        ).execute()

        lote = respuesta.data or []
        registros.extend(lote)

        if len(lote) < TAMANO_PAGINA:
            break

        inicio += TAMANO_PAGINA

    return registros


def cargar_pedidos():
    return leer_tabla("pedidos", orden="fecha", descendente=True)


def cargar_detalles(ids_pedidos):
    if not ids_pedidos:
        return []

    detalles = []

    # Divide la consulta en grupos para no enviar listas enormes.
    for inicio in range(0, len(ids_pedidos), 200):
        grupo = ids_pedidos[inicio:inicio + 200]
        respuesta = (
            supabase.table("detalle_pedido")
            .select("*")
            .in_("pedido_id", grupo)
            .execute()
        )
        detalles.extend(respuesta.data or [])

    return detalles


def cargar_catalogo(solo_activos=False):
    consulta = supabase.table("catalogo_platos").select("*")

    if solo_activos:
        consulta = consulta.eq("activo", True)

    respuesta = consulta.order("tipo").order("nombre").execute()
    return respuesta.data or []


def obtener_detalles_por_pedido(detalles):
    resultado = {}

    for detalle in detalles:
        pedido_id = detalle.get("pedido_id")
        resultado.setdefault(pedido_id, []).append(detalle)

    return resultado


def detalles_de_pedido(detalles_por_id, pedido_id, tipo):
    filas = detalles_por_id.get(pedido_id, [])

    return normalizar_platos([
        fila.get("plato", "")
        for fila in filas
        if fila.get("tipo") == tipo
    ])


def calcular_total(precio, cantidad):
    return round(float(precio) * int(cantidad), 2)


def guardar_detalles(pedido_id, entradas, segundos):
    filas = []

    for plato in normalizar_platos(entradas):
        filas.append({
            "pedido_id": pedido_id,
            "tipo": "Entrada",
            "plato": plato,
            "cantidad": 1,
        })

    for plato in normalizar_platos(segundos):
        filas.append({
            "pedido_id": pedido_id,
            "tipo": "Segundo",
            "plato": plato,
            "cantidad": 1,
        })

    if filas:
        supabase.table("detalle_pedido").insert(filas).execute()


def validar_pedido(cliente, precio, cantidad):
    if not cliente:
        return "Escribe el nombre del cliente."

    if precio < PRECIO_MINIMO or precio > PRECIO_MAXIMO:
        return (
            f"El precio por menú debe estar entre "
            f"{dinero(PRECIO_MINIMO)} y {dinero(PRECIO_MAXIMO)}."
        )

    if cantidad < 1:
        return "La cantidad de menús debe ser como mínimo 1."

    if cantidad > 10000:
        return "La cantidad es demasiado grande. Comprueba el dato."

    return None


def texto_fecha(valor):
    if not valor:
        return ""

    try:
        return pd.to_datetime(valor).strftime("%d/%m/%Y")
    except Exception:
        return str(valor)


def preparar_dataframe(pedidos):
    columnas = [
        "id", "fecha", "cliente", "empresa",
        "precio_menu", "cantidad_menus", "total", "observaciones"
    ]

    if not pedidos:
        return pd.DataFrame(columns=columnas)

    df = pd.DataFrame(pedidos)

    for columna in columnas:
        if columna not in df.columns:
            df[columna] = None

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    df["cliente"] = df["cliente"].fillna("").astype(str)
    df["empresa"] = df["empresa"].fillna("").astype(str)
    df["precio_menu"] = pd.to_numeric(df["precio_menu"], errors="coerce").fillna(0)
    df["cantidad_menus"] = pd.to_numeric(
        df["cantidad_menus"], errors="coerce"
    ).fillna(0)
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)

    return df


def filtrar_por_fechas(df, inicio, fin):
    if df.empty:
        return df.copy()

    return df[
        (df["fecha"] >= inicio) &
        (df["fecha"] <= fin)
    ].copy()


def calcular_indicadores(df):
    if df.empty:
        return {
            "ventas": 0.0,
            "pedidos": 0,
            "menus": 0,
            "promedio": 0.0,
        }

    ventas = float(df["total"].sum())
    cantidad_pedidos = int(len(df))
    menus = int(df["cantidad_menus"].sum())

    return {
        "ventas": ventas,
        "pedidos": cantidad_pedidos,
        "menus": menus,
        "promedio": ventas / cantidad_pedidos if cantidad_pedidos else 0,
    }


# ============================================================
# 3. CONEXIÓN A SUPABASE
# ============================================================

try:
    URL_SUPABASE = str(st.secrets["SUPABASE_URL"]).strip().rstrip("/")
    CLAVE_SUPABASE = str(st.secrets["SUPABASE_KEY"]).strip()

    partes_url = urlparse(URL_SUPABASE)

    if (
        partes_url.scheme != "https"
        or not partes_url.hostname
        or not partes_url.hostname.endswith(".supabase.co")
        or partes_url.path not in ("", "/")
        or partes_url.query
        or partes_url.fragment
    ):
        raise ValueError(
            "SUPABASE_URL debe ser la URL base del proyecto, "
            "por ejemplo https://xxxx.supabase.co, sin rutas adicionales."
        )

    supabase = create_client(URL_SUPABASE, CLAVE_SUPABASE)

except Exception as error:
    st.title("🍽️ Como en Casa Dely")
    mostrar_error(
        "No se pudo establecer la conexión con Supabase. "
        "Revisa los secretos de Streamlit.",
        error,
    )
    st.stop()


# ============================================================
# 4. AUTENTICACIÓN
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if "confirmar_eliminacion" not in st.session_state:
    st.session_state.confirmar_eliminacion = None


def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.pagina = "Inicio"
    st.rerun()


if not st.session_state.autenticado:
    mostrar_marca()

    st.subheader("Acceso privado")

    with st.form("form_login"):
        contrasena = st.text_input(
            "Contraseña",
            type="password",
            placeholder="Introduce tu contraseña",
        )
        entrar = st.form_submit_button(
            "Ingresar",
            type="primary",
            use_container_width=True,
        )

    if entrar:
        try:
            contrasena_correcta = str(st.secrets["APP_PASSWORD"])

            if contrasena and contrasena == contrasena_correcta:
                st.session_state.autenticado = True
                registrar_evento("INFO", "Inicio de sesión", "Acceso correcto")
                st.rerun()
            else:
                st.error("La contraseña no es correcta.")
        except Exception as error:
            mostrar_error("No se encontró APP_PASSWORD en los secretos.", error)

    st.stop()


# ============================================================
# 5. MENÚ LATERAL
# ============================================================

paginas = [
    ("🏠", "Inicio"),
    ("➕", "Registrar pedido"),
    ("📋", "Pedidos"),
    ("📊", "Estadísticas"),
    ("🍲", "Catálogo"),
    ("🏢", "Empresas"),
    ("🛠️", "Sistema"),
]

with st.sidebar:
    st.markdown("## 🍽️ Como en Casa Dely")
    st.caption(f"Versión {VERSION_APP}")
    st.divider()

    for icono, nombre in paginas:
        if st.button(
            f"{icono}  {nombre}",
            key=f"nav_{nombre}",
            use_container_width=True,
        ):
            st.session_state.pagina = nombre
            st.rerun()

    st.divider()
    st.caption(f"Fecha de Perú: {hoy_peru().strftime('%d/%m/%Y')}")

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        cerrar_sesion()


pagina = st.session_state.pagina


# ============================================================
# 6. CARGA DE DATOS
# ============================================================

try:
    pedidos = cargar_pedidos()
    df_pedidos = preparar_dataframe(pedidos)

except Exception as error:
    registrar_evento("ERROR", "Cargar pedidos", error)
    mostrar_error(
        "No se pudieron cargar los pedidos. "
        "Comprueba que la tabla public.pedidos conserve sus columnas.",
        error,
    )
    st.stop()


# ============================================================
# 7. INICIO / PANEL DE CONTROL
# ============================================================

if pagina == "Inicio":
    mostrar_marca()
    st.subheader("Panel de control")

    hoy = hoy_peru()
    df_hoy = df_pedidos[df_pedidos["fecha"] == hoy].copy()
    indicadores_hoy = calcular_indicadores(df_hoy)
    indicadores_total = calcular_indicadores(df_pedidos)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ventas de hoy", dinero(indicadores_hoy["ventas"]))
    c2.metric("Pedidos de hoy", indicadores_hoy["pedidos"])
    c3.metric("Menús de hoy", indicadores_hoy["menus"])
    c4.metric("Empresas atendidas", int(
        df_hoy.loc[df_hoy["empresa"].str.strip() != "", "empresa"]
        .nunique()
    ))

    st.divider()
    st.subheader("Acumulado registrado")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Ventas acumuladas", dinero(indicadores_total["ventas"]))
    a2.metric("Pedidos acumulados", indicadores_total["pedidos"])
    a3.metric("Menús acumulados", indicadores_total["menus"])
    a4.metric("Promedio por pedido", dinero(indicadores_total["promedio"]))

    st.divider()

    if not df_pedidos.empty:
        st.subheader("Ventas por día")

        ventas_dia = (
            df_pedidos.groupby("fecha", as_index=False)["total"]
            .sum()
            .sort_values("fecha")
            .tail(30)
        )

        ventas_dia["fecha"] = ventas_dia["fecha"].astype(str)
        ventas_dia = ventas_dia.set_index("fecha")
        st.bar_chart(ventas_dia["total"])

        empresas = df_pedidos[
            df_pedidos["empresa"].str.strip() != ""
        ].copy()

        if not empresas.empty:
            st.subheader("Ventas por empresa")

            ventas_empresa = (
                empresas.groupby("empresa", as_index=False)["total"]
                .sum()
                .sort_values("total", ascending=False)
            )

            st.bar_chart(ventas_empresa.set_index("empresa")["total"])

        st.subheader("Pedidos recientes")
        recientes = df_pedidos.head(10).copy()

        recientes["fecha"] = recientes["fecha"].apply(texto_fecha)
        recientes["total"] = recientes["total"].apply(dinero)

        st.dataframe(
            recientes[
                ["id", "fecha", "cliente", "empresa",
                 "cantidad_menus", "total"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Todavía no hay pedidos registrados.")

    st.caption(
        "Los acumulados corresponden a los pedidos que existen "
        "actualmente en la base de datos de Supabase."
    )


# ============================================================
# 8. REGISTRAR PEDIDO
# ============================================================

elif pagina == "Registrar pedido":
    mostrar_marca()
    st.subheader("Registrar nuevo pedido")

    try:
        catalogo_activo = cargar_catalogo(solo_activos=True)
    except Exception as error:
        registrar_evento("ERROR", "Leer catálogo", error)
        catalogo_activo = []
        st.warning(
            "No se pudo leer el catálogo. Puedes escribir los platos "
            "manualmente y revisar la sección Catálogo."
        )

    entradas_catalogo = sorted(set(
        fila["nombre"] for fila in catalogo_activo
        if fila.get("tipo") == "Entrada"
    ))

    segundos_catalogo = sorted(set(
        fila["nombre"] for fila in catalogo_activo
        if fila.get("tipo") == "Segundo"
    ))

    empresas_existentes = sorted(set(
        nombre.strip()
        for nombre in df_pedidos["empresa"].tolist()
        if str(nombre).strip()
    ))

    with st.form("form_registrar_pedido", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            fecha_pedido = st.date_input(
                "Fecha del pedido",
                value=hoy_peru(),
            )
            cliente = st.text_input(
                "Nombre del cliente *",
                placeholder="Nombre del cliente",
            )
            empresa_seleccion = st.selectbox(
                "Empresa",
                ["Sin empresa registrada"] + empresas_existentes + ["Otra empresa"],
            )

            if empresa_seleccion == "Otra empresa":
                empresa = st.text_input("Nombre de la nueva empresa")
            elif empresa_seleccion == "Sin empresa registrada":
                empresa = ""
            else:
                empresa = empresa_seleccion

        with c2:
            precio = st.number_input(
                "Precio por menú (S/)",
                min_value=PRECIO_MINIMO,
                max_value=PRECIO_MAXIMO,
                value=15.0,
                step=0.5,
            )
            cantidad = st.number_input(
                "Cantidad de menús",
                min_value=1,
                max_value=10000,
                value=1,
                step=1,
            )
            st.metric(
                "Total calculado",
                dinero(calcular_total(precio, cantidad)),
            )

        st.markdown("#### 🍲 Menú")

        entradas_seleccionadas = st.multiselect(
            "Entradas",
            options=entradas_catalogo,
            help="Puedes elegir varias entradas del catálogo.",
        )

        entradas_extra_texto = st.text_area(
            "Otras entradas (opcional)",
            placeholder="Escribe platos separados por comas o líneas",
        )

        segundos_seleccionados = st.multiselect(
            "Segundos",
            options=segundos_catalogo,
            help="Puedes elegir varios segundos del catálogo.",
        )

        segundos_extra_texto = st.text_area(
            "Otros segundos (opcional)",
            placeholder="Escribe platos separados por comas o líneas",
        )

        direccion = st.text_input(
            "Dirección de entrega",
            placeholder="Dirección completa",
        )
        observaciones = st.text_area(
            "Observaciones",
            placeholder="Indicaciones, cambios o comentarios",
        )

        guardar = st.form_submit_button(
            "💾 Guardar pedido",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        cliente = limpiar_texto(cliente)
        empresa = limpiar_texto(empresa)
        direccion = limpiar_texto(direccion)
        observaciones = limpiar_texto(observaciones)

        error_validacion = validar_pedido(cliente, precio, cantidad)

        entradas_finales = normalizar_platos(
            entradas_seleccionadas + separar_platos(entradas_extra_texto)
        )
        segundos_finales = normalizar_platos(
            segundos_seleccionados + separar_platos(segundos_extra_texto)
        )

        if error_validacion:
            st.error(error_validacion)
        else:
            try:
                total = calcular_total(precio, cantidad)

                nuevo_pedido = {
                    "fecha": fecha_pedido.isoformat(),
                    "cliente": cliente,
                    "empresa": empresa,
                    "precio_menu": float(precio),
                    "cantidad_menus": int(cantidad),
                    "total": total,
                    "observaciones": observaciones,
                }

                # Dirección se guarda en observaciones para conservar
                # compatibilidad con la tabla actual, sin perder datos.
                if direccion:
                    texto_direccion = f"Dirección: {direccion}"
                    nuevo_pedido["observaciones"] = (
                        f"{texto_direccion}\n{observaciones}".strip()
                    )

                respuesta = (
                    supabase.table("pedidos")
                    .insert(nuevo_pedido)
                    .execute()
                )

                if not respuesta.data:
                    raise RuntimeError(
                        "Supabase no devolvió el pedido creado."
                    )

                pedido_id = respuesta.data[0]["id"]

                try:
                    guardar_detalles(
                        pedido_id,
                        entradas_finales,
                        segundos_finales,
                    )
                except Exception as error_detalle:
                    # El pedido principal ya existe; no fingir que todo
                    # se guardó correctamente.
                    registrar_evento(
                        "ERROR",
                        "Guardar detalles del pedido",
                        f"Pedido {pedido_id}: {error_detalle}",
                    )
                    st.warning(
                        f"El pedido #{pedido_id} se guardó, pero hubo "
                        "un problema al guardar sus platos. Entra a "
                        "Pedidos y revisa sus detalles."
                    )
                else:
                    registrar_evento(
                        "INFO",
                        "Crear pedido",
                        f"Pedido #{pedido_id}; cliente={cliente}; total={total}",
                    )
                    st.success(
                        f"Pedido #{pedido_id} guardado. Total: {dinero(total)}"
                    )

                st.rerun()

            except Exception as error:
                registrar_evento("ERROR", "Crear pedido", error)
                mostrar_error(
                    "No se pudo guardar el pedido. No vuelvas a pulsar "
                    "Guardar repetidamente sin comprobar primero si ya "
                    "se creó en la sección Pedidos.",
                    error,
                )


# ============================================================
# 9. HISTORIAL, EDICIÓN Y ELIMINACIÓN
# ============================================================

elif pagina == "Pedidos":
    mostrar_marca()
    st.subheader("Historial y administración de pedidos")

    if df_pedidos.empty:
        st.info("No hay pedidos registrados.")
    else:
        with st.expander("🔎 Filtros", expanded=True):
            f1, f2 = st.columns(2)

            fecha_minima = min(df_pedidos["fecha"].dropna())
            fecha_maxima = max(df_pedidos["fecha"].dropna())

            with f1:
                rango = st.date_input(
                    "Rango de fechas",
                    value=(fecha_minima, fecha_maxima),
                )

            with f2:
                filtro_cliente = st.text_input(
                    "Buscar cliente",
                    placeholder="Nombre parcial",
                )
                lista_empresas = sorted(set(
                    x for x in df_pedidos["empresa"].tolist() if x
                ))
                filtro_empresa = st.selectbox(
                    "Empresa",
                    ["Todas"] + lista_empresas,
                )

        df_filtrado = df_pedidos.copy()

        if isinstance(rango, (tuple, list)) and len(rango) == 2:
            df_filtrado = filtrar_por_fechas(
                df_filtrado, rango[0], rango[1]
            )

        if filtro_cliente.strip():
            df_filtrado = df_filtrado[
                df_filtrado["cliente"].str.contains(
                    filtro_cliente.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ]

        if filtro_empresa != "Todas":
            df_filtrado = df_filtrado[
                df_filtrado["empresa"] == filtro_empresa
            ]

        metricas = calcular_indicadores(df_filtrado)
        m1, m2, m3 = st.columns(3)
        m1.metric("Ventas filtradas", dinero(metricas["ventas"]))
        m2.metric("Pedidos encontrados", metricas["pedidos"])
        m3.metric("Menús encontrados", metricas["menus"])

        tabla = df_filtrado.copy()
        tabla["fecha"] = tabla["fecha"].apply(texto_fecha)
        tabla["total"] = tabla["total"].apply(dinero)
        tabla["precio_menu"] = tabla["precio_menu"].apply(dinero)

        st.dataframe(
            tabla[
                ["id", "fecha", "cliente", "empresa", "precio_menu",
                 "cantidad_menus", "total", "observaciones"]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Exportar pedidos filtrados a CSV",
            data=df_filtrado.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"pedidos_{hoy_peru().isoformat()}.csv",
            mime="text/csv",
            use_container_width=False,
        )

        st.divider()
        st.subheader("Editar o eliminar un pedido")

        ids_disponibles = df_filtrado["id"].tolist()

        if not ids_disponibles:
            st.info("No hay pedidos que coincidan con los filtros.")
        else:
            id_seleccionado = st.selectbox(
                "Selecciona el número de pedido",
                ids_disponibles,
                format_func=lambda x: (
                    f"Pedido #{x} — "
                    f"{df_filtrado.loc[df_filtrado['id'] == x, 'cliente'].iloc[0]}"
                ),
            )

            pedido_actual = next(
                p for p in pedidos if p.get("id") == id_seleccionado
            )

            try:
                detalles_actuales = cargar_detalles([id_seleccionado])
            except Exception as error:
                detalles_actuales = []
                mostrar_error("No se pudieron leer los platos del pedido.", error)

            entradas_actuales = normalizar_platos([
                d.get("plato", "")
                for d in detalles_actuales
                if d.get("tipo") == "Entrada"
            ])

            segundos_actuales = normalizar_platos([
                d.get("plato", "")
                for d in detalles_actuales
                if d.get("tipo") == "Segundo"
            ])

            try:
                catalogo_activo = cargar_catalogo(solo_activos=True)
            except Exception:
                catalogo_activo = []

            opciones_entradas = sorted(set(
                entradas_actuales + [
                    f["nombre"] for f in catalogo_activo
                    if f.get("tipo") == "Entrada"
                ]
            ))

            opciones_segundos = sorted(set(
                segundos_actuales + [
                    f["nombre"] for f in catalogo_activo
                    if f.get("tipo") == "Segundo"
                ]
            ))

            with st.expander("✏️ Editar pedido", expanded=False):
                with st.form(f"editar_{id_seleccionado}"):
                    ec1, ec2 = st.columns(2)

                    with ec1:
                        e_fecha = st.date_input(
                            "Fecha",
                            value=pd.to_datetime(
                                pedido_actual.get("fecha")
                            ).date(),
                            key=f"e_fecha_{id_seleccionado}",
                        )
                        e_cliente = st.text_input(
                            "Cliente",
                            value=pedido_actual.get("cliente", ""),
                            key=f"e_cliente_{id_seleccionado}",
                        )
                        e_empresa = st.text_input(
                            "Empresa",
                            value=pedido_actual.get("empresa", "") or "",
                            key=f"e_empresa_{id_seleccionado}",
                        )

                    with ec2:
                        e_precio = st.number_input(
                            "Precio por menú",
                            min_value=PRECIO_MINIMO,
                            max_value=PRECIO_MAXIMO,
                            value=float(pedido_actual.get("precio_menu") or 15),
                            step=0.5,
                            key=f"e_precio_{id_seleccionado}",
                        )
                        e_cantidad = st.number_input(
                            "Cantidad de menús",
                            min_value=1,
                            max_value=10000,
                            value=max(
                                1,
                                int(pedido_actual.get("cantidad_menus") or 1),
                            ),
                            key=f"e_cantidad_{id_seleccionado}",
                        )

                    e_entradas = st.multiselect(
                        "Entradas",
                        options=opciones_entradas,
                        default=entradas_actuales,
                        key=f"e_entradas_{id_seleccionado}",
                    )

                    e_segundos = st.multiselect(
                        "Segundos",
                        options=opciones_segundos,
                        default=segundos_actuales,
                        key=f"e_segundos_{id_seleccionado}",
                    )

                    e_observaciones = st.text_area(
                        "Observaciones",
                        value=pedido_actual.get("observaciones", "") or "",
                        key=f"e_obs_{id_seleccionado}",
                    )

                    st.caption(
                        "El total se recalcula automáticamente como "
                        "precio por menú × cantidad de menús."
                    )
                    st.write(
                        "Nuevo total: ",
                        dinero(calcular_total(e_precio, e_cantidad)),
                    )

                    guardar_edicion = st.form_submit_button(
                        "Guardar cambios",
                        type="primary",
                        use_container_width=True,
                    )

                if guardar_edicion:
                    error_validacion = validar_pedido(
                        e_cliente, e_precio, e_cantidad
                    )

                    if error_validacion:
                        st.error(error_validacion)
                    else:
                        try:
                            datos_actualizados = {
                                "fecha": e_fecha.isoformat(),
                                "cliente": limpiar_texto(e_cliente),
                                "empresa": limpiar_texto(e_empresa),
                                "precio_menu": float(e_precio),
                                "cantidad_menus": int(e_cantidad),
                                "total": calcular_total(e_precio, e_cantidad),
                                "observaciones": limpiar_texto(e_observaciones),
                            }

                            # Actualiza el pedido principal.
                            (
                                supabase.table("pedidos")
                                .update(datos_actualizados)
                                .eq("id", id_seleccionado)
                                .execute()
                            )

                            # Reemplaza los detalles de forma controlada.
                            (
                                supabase.table("detalle_pedido")
                                .delete()
                                .eq("pedido_id", id_seleccionado)
                                .execute()
                            )

                            guardar_detalles(
                                id_seleccionado,
                                e_entradas,
                                e_segundos,
                            )

                            registrar_evento(
                                "INFO",
                                "Editar pedido",
                                f"Pedido #{id_seleccionado}",
                            )
                            st.success("Pedido actualizado.")
                            st.rerun()

                        except Exception as error:
                            registrar_evento("ERROR", "Editar pedido", error)
                            mostrar_error(
                                "No se pudieron completar todos los cambios. "
                                "Comprueba el pedido y sus detalles antes de "
                                "volver a intentarlo.",
                                error,
                            )

            with st.expander("🗑️ Eliminar pedido", expanded=False):
                st.warning(
                    "Esta operación elimina el pedido y sus platos asociados. "
                    "No se puede deshacer."
                )

                confirmar = st.checkbox(
                    f"Confirmo que quiero eliminar el pedido #{id_seleccionado}",
                    key=f"confirmar_{id_seleccionado}",
                )

                if st.button(
                    "Eliminar definitivamente",
                    type="primary",
                    key=f"eliminar_{id_seleccionado}",
                    disabled=not confirmar,
                ):
                    try:
                        (
                            supabase.table("detalle_pedido")
                            .delete()
                            .eq("pedido_id", id_seleccionado)
                            .execute()
                        )

                        (
                            supabase.table("pedidos")
                            .delete()
                            .eq("id", id_seleccionado)
                            .execute()
                        )

                        registrar_evento(
                            "INFO",
                            "Eliminar pedido",
                            f"Pedido #{id_seleccionado}",
                        )
                        st.success("Pedido eliminado.")
                        st.rerun()

                    except Exception as error:
                        registrar_evento("ERROR", "Eliminar pedido", error)
                        mostrar_error(
                            "No se pudo eliminar el pedido completamente. "
                            "Comprueba el historial antes de volver a intentarlo.",
                            error,
                        )


# ============================================================
# 10. ESTADÍSTICAS Y RESÚMENES POR FECHA
# ============================================================

elif pagina == "Estadísticas":
    mostrar_marca()
    st.subheader("Estadísticas y resumen histórico")

    if df_pedidos.empty:
        st.info("Cuando registres pedidos, aquí aparecerán las estadísticas.")
    else:
        fecha_minima = min(df_pedidos["fecha"].dropna())
        fecha_maxima = max(df_pedidos["fecha"].dropna())

        s1, s2 = st.columns(2)

        with s1:
            fecha_inicio = st.date_input(
                "Desde",
                value=fecha_minima,
                key="stats_inicio",
            )

        with s2:
            fecha_fin = st.date_input(
                "Hasta",
                value=fecha_maxima,
                key="stats_fin",
            )

        if fecha_inicio > fecha_fin:
            st.error("La fecha inicial no puede ser posterior a la final.")
        else:
            df_periodo = filtrar_por_fechas(
                df_pedidos, fecha_inicio, fecha_fin
            )

            resumen = calcular_indicadores(df_periodo)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Ventas", dinero(resumen["ventas"]))
            c2.metric("Pedidos", resumen["pedidos"])
            c3.metric("Menús", resumen["menus"])
            c4.metric("Promedio por pedido", dinero(resumen["promedio"]))

            st.divider()
            st.subheader("Resumen por día")

            if not df_periodo.empty:
                por_dia = (
                    df_periodo.groupby("fecha", as_index=False)
                    .agg(
                        ventas=("total", "sum"),
                        pedidos=("id", "count"),
                        menus=("cantidad_menus", "sum"),
                    )
                    .sort_values("fecha")
                )

                por_dia["fecha"] = por_dia["fecha"].astype(str)
                st.dataframe(
                    por_dia,
                    use_container_width=True,
                    hide_index=True,
                )

                st.line_chart(por_dia.set_index("fecha")["ventas"])

                st.subheader("Resumen por empresa")

                por_empresa = (
                    df_periodo.assign(
                        empresa=df_periodo["empresa"].replace("", "Sin empresa")
                    )
                    .groupby("empresa", as_index=False)
                    .agg(
                        ventas=("total", "sum"),
                        pedidos=("id", "count"),
                        menus=("cantidad_menus", "sum"),
                    )
                    .sort_values("ventas", ascending=False)
                )

                st.dataframe(
                    por_empresa,
                    use_container_width=True,
                    hide_index=True,
                )

                st.subheader("Resumen por cliente")

                por_cliente = (
                    df_periodo.groupby("cliente", as_index=False)
                    .agg(
                        ventas=("total", "sum"),
                        pedidos=("id", "count"),
                        menus=("cantidad_menus", "sum"),
                    )
                    .sort_values("ventas", ascending=False)
                )

                st.dataframe(
                    por_cliente,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No hay pedidos en el período seleccionado.")

            st.download_button(
                "⬇️ Descargar resumen del período",
                data=df_periodo.to_csv(index=False).encode("utf-8-sig"),
                file_name=(
                    f"resumen_{fecha_inicio.isoformat()}_"
                    f"{fecha_fin.isoformat()}.csv"
                ),
                mime="text/csv",
            )


# ============================================================
# 11. CATÁLOGO DE ENTRADAS Y SEGUNDOS
# ============================================================

elif pagina == "Catálogo":
    mostrar_marca()
    st.subheader("Catálogo de platos")

    st.markdown(
        '<div class="nota">Aquí puedes administrar las entradas y los segundos. '
        'Desactivar un plato lo oculta de los nuevos pedidos, pero no elimina '
        'su nombre de los pedidos históricos.</div>',
        unsafe_allow_html=True,
    )

    try:
        catalogo = cargar_catalogo(solo_activos=False)
    except Exception as error:
        mostrar_error(
            "No se pudo abrir el catálogo. Confirma que ejecutaste el SQL "
            "de creación de tablas.",
            error,
        )
        st.stop()

    with st.expander("➕ Agregar plato", expanded=True):
        with st.form("form_nuevo_plato"):
            tipo_nuevo = st.selectbox(
                "Tipo",
                ["Entrada", "Segundo"],
            )
            nombre_nuevo = st.text_input(
                "Nombre del plato",
                placeholder="Ej.: nombre del plato",
            )
            crear_plato = st.form_submit_button(
                "Agregar al catálogo",
                type="primary",
            )

        if crear_plato:
            nombre_nuevo = limpiar_texto(nombre_nuevo)

            if not nombre_nuevo:
                st.error("Escribe el nombre del plato.")
            elif len(nombre_nuevo) > 150:
                st.error("El nombre no puede superar 150 caracteres.")
            else:
                try:
                    existe = any(
                        f.get("tipo") == tipo_nuevo
                        and limpiar_texto(f.get("nombre")).casefold()
                        == nombre_nuevo.casefold()
                        for f in catalogo
                    )

                    if existe:
                        st.warning("Ese plato ya existe en ese tipo.")
                    else:
                        supabase.table("catalogo_platos").insert({
                            "tipo": tipo_nuevo,
                            "nombre": nombre_nuevo,
                            "activo": True,
                        }).execute()

                        registrar_evento(
                            "INFO",
                            "Crear plato",
                            f"{tipo_nuevo}: {nombre_nuevo}",
                        )
                        st.success("Plato agregado.")
                        st.rerun()

                except Exception as error:
                    registrar_evento("ERROR", "Crear plato", error)
                    mostrar_error("No se pudo agregar el plato.", error)

    st.divider()
    st.subheader("Platos registrados")

    if not catalogo:
        st.info("El catálogo está vacío. Agrega tus platos arriba.")
    else:
        df_catalogo = pd.DataFrame(catalogo)
        df_catalogo["estado"] = df_catalogo["activo"].map({
            True: "Activo",
            False: "Inactivo",
        })

        st.dataframe(
            df_catalogo[["id", "tipo", "nombre", "estado"]],
            use_container_width=True,
            hide_index=True,
        )

        ids_catalogo = [fila["id"] for fila in catalogo]

        id_plato = st.selectbox(
            "Selecciona un plato para editar",
            ids_catalogo,
            format_func=lambda x: (
                f"#{x} — "
                f"{next(f['nombre'] for f in catalogo if f['id'] == x)}"
            ),
        )

        plato_actual = next(f for f in catalogo if f["id"] == id_plato)

        with st.form(f"editar_plato_{id_plato}"):
            tipo_editar = st.selectbox(
                "Tipo de plato",
                ["Entrada", "Segundo"],
                index=0 if plato_actual["tipo"] == "Entrada" else 1,
            )
            nombre_editar = st.text_input(
                "Nombre",
                value=plato_actual["nombre"],
            )
            activo_editar = st.checkbox(
                "Disponible para nuevos pedidos",
                value=bool(plato_actual["activo"]),
            )

            guardar_plato = st.form_submit_button(
                "Guardar cambios del plato",
                type="primary",
            )

        if guardar_plato:
            nombre_editar = limpiar_texto(nombre_editar)

            if not nombre_editar:
                st.error("El nombre no puede quedar vacío.")
            elif len(nombre_editar) > 150:
                st.error("El nombre no puede superar 150 caracteres.")
            else:
                try:
                    (
                        supabase.table("catalogo_platos")
                        .update({
                            "tipo": tipo_editar,
                            "nombre": nombre_editar,
                            "activo": activo_editar,
                        })
                        .eq("id", id_plato)
                        .execute()
                    )

                    registrar_evento(
                        "INFO",
                        "Editar plato",
                        f"Plato #{id_plato}: {nombre_editar}",
                    )
                    st.success("Catálogo actualizado.")
                    st.rerun()

                except Exception as error:
                    registrar_evento("ERROR", "Editar plato", error)
                    mostrar_error(
                        "No se pudo actualizar el plato. "
                        "Comprueba que no exista otro con el mismo nombre y tipo.",
                        error,
                    )


# ============================================================
# 12. ADMINISTRACIÓN DE EMPRESAS
# ============================================================

elif pagina == "Empresas":
    mostrar_marca()
    st.subheader("Administración de empresas")

    st.write(
        "Las empresas se obtienen de los pedidos existentes. "
        "No necesitas registrar una empresa por separado para poder usarla "
        "al crear un pedido."
    )

    df_empresas = df_pedidos.copy()
    df_empresas["empresa"] = df_empresas["empresa"].replace("", "Sin empresa")

    if df_empresas.empty:
        st.info("Todavía no existen pedidos para agrupar por empresa.")
    else:
        resumen_empresas = (
            df_empresas.groupby("empresa", as_index=False)
            .agg(
                ventas=("total", "sum"),
                pedidos=("id", "count"),
                menus=("cantidad_menus", "sum"),
            )
            .sort_values("ventas", ascending=False)
        )

        st.dataframe(
            resumen_empresas,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.subheader("Corregir o unificar el nombre de una empresa")

    empresas_existentes = sorted(set(
        limpiar_texto(x)
        for x in df_pedidos["empresa"].tolist()
        if limpiar_texto(x)
    ))

    if not empresas_existentes:
        st.info("No hay nombres de empresas registrados para modificar.")
    else:
        with st.form("form_renombrar_empresa"):
            empresa_antigua = st.selectbox(
                "Nombre actual",
                empresas_existentes,
            )
            empresa_nueva = st.text_input(
                "Nombre correcto",
                placeholder="Escribe el nombre que quieres usar",
            )
            renombrar = st.form_submit_button(
                "Actualizar empresa en todos sus pedidos",
                type="primary",
            )

        if renombrar:
            empresa_nueva = limpiar_texto(empresa_nueva)

            if not empresa_nueva:
                st.error("El nuevo nombre no puede quedar vacío.")
            elif empresa_nueva == empresa_antigua:
                st.info("El nombre no ha cambiado.")
            else:
                st.warning(
                    f"Se cambiará {empresa_antigua!r} por "
                    f"{empresa_nueva!r} en todos sus pedidos."
                )

                confirmar_empresa = st.checkbox(
                    "Confirmo que deseo aplicar este cambio global",
                    key="confirmar_empresa_global",
                )

                if confirmar_empresa:
                    try:
                        (
                            supabase.table("pedidos")
                            .update({"empresa": empresa_nueva})
                            .eq("empresa", empresa_antigua)
                            .execute()
                        )

                        registrar_evento(
                            "INFO",
                            "Renombrar empresa",
                            f"{empresa_antigua} → {empresa_nueva}",
                        )
                        st.success("Se actualizó el nombre de la empresa.")
                        st.rerun()

                    except Exception as error:
                        registrar_evento("ERROR", "Renombrar empresa", error)
                        mostrar_error(
                            "No se pudo actualizar el nombre de la empresa.",
                            error,
                        )


# ============================================================
# 13. SISTEMA, REGISTRO DE EVENTOS Y VERSIÓN
# ============================================================

elif pagina == "Sistema":
    mostrar_marca()
    st.subheader("Estado del sistema")

    st.metric("Versión de la aplicación", VERSION_APP)
    st.metric("Pedidos disponibles", len(df_pedidos))

    st.write("**Conexión a Supabase:** configurada")
    st.write("**Fecha local:**", hoy_peru().strftime("%d/%m/%Y"))

    st.divider()
    st.subheader("Registro de eventos")

    try:
        eventos = leer_tabla(
            "registro_sistema",
            orden="fecha",
            descendente=True,
        )

        if eventos:
            df_eventos = pd.DataFrame(eventos)
            columnas_eventos = [
                c for c in ["fecha", "nivel", "operacion", "detalle"]
                if c in df_eventos.columns
            ]
            st.dataframe(
                df_eventos[columnas_eventos].head(200),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Todavía no hay eventos registrados.")

    except Exception as error:
        mostrar_error(
            "No se pudo leer el registro de eventos. "
            "Confirma que creaste public.registro_sistema.",
            error,
        )

    st.divider()
    st.subheader("Comprobaciones")

    if st.button("Comprobar acceso a las tablas", type="primary"):
        resultados = []

        for tabla in [
            "pedidos",
            "detalle_pedido",
            "catalogo_platos",
            "registro_sistema",
        ]:
            try:
                supabase.table(tabla).select("*").limit(1).execute()
                resultados.append((tabla, "Correcto"))
            except Exception as error:
                resultados.append((tabla, f"Error: {error}"))

        for tabla, resultado in resultados:
            if resultado == "Correcto":
                st.success(f"{tabla}: {resultado}")
            else:
                st.error(f"{tabla}: {resultado}")


# ============================================================
# 14. PIE DE PÁGINA
# ============================================================

st.divider()
st.caption(
    f"{NOMBRE_APP} · Versión {VERSION_APP} · "
    "Gestión de pedidos y ventas"
)
