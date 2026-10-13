import re
from datetime import date, datetime
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
VERSION_APP = "3.0.0"
PRECIO_MINIMO = 10.0
PRECIO_MAXIMO = 20.0
TAMANO_PAGINA = 1000


# ============================================================
# 2. DISEÑO MADERA NATURAL
# ============================================================

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
        --texto: #35291F;
        --borde: #D9C5A9;
    }

    .stApp {
        background: var(--crema);
        color: var(--texto);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4A3425, #65472F);
    }

    [data-testid="stSidebar"] * {
        color: #FFF8EC;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: 100%;
        text-align: left;
        background: #62462F;
        border: 1px solid #977655;
        color: #FFF8EC;
        border-radius: 12px;
        min-height: 46px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background: #8B6946;
        border-color: #D9BE99;
    }

    h1, h2, h3 {
        color: var(--madera-oscura);
        font-family: 'Playfair Display', serif;
    }

    [data-testid="stMetric"] {
        background: #FFFCF6;
        border: 1px solid var(--borde);
        padding: 16px;
        border-radius: 15px;
        box-shadow: 0 3px 10px rgba(74, 52, 37, .05);
    }

    [data-testid="stMetricLabel"] {
        color: #765D46;
    }

    [data-testid="stMetricValue"] {
        color: var(--madera);
        font-weight: 700;
    }

    div[data-testid="stForm"] {
        background: #FFFCF6;
        border: 1px solid var(--borde);
        padding: 18px;
        border-radius: 16px;
    }

    .marca {
        background:
            linear-gradient(115deg, rgba(63,43,29,.97), rgba(121,84,56,.94)),
            repeating-linear-gradient(
                0deg, #795438, #795438 5px, #8D6747 6px, #795438 10px
            );
        color: #FFF8EC;
        padding: 25px;
        border-radius: 18px;
        margin-bottom: 20px;
        border: 1px solid #A9825B;
    }

    .marca h1 {
        color: #FFF8EC;
        margin: 0;
        font-size: 30px;
    }

    .marca p {
        color: #EAD8BF;
        margin: 7px 0 0;
    }

    .nota {
        background: #F0E4D1;
        border-left: 4px solid #795438;
        padding: 13px 16px;
        border-radius: 8px;
        color: #4A3425;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button {
        background: #795438;
        border-color: #795438;
        color: white;
        border-radius: 10px;
        font-weight: 700;
        min-height: 42px;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button:hover {
        background: #4A3425;
        border-color: #4A3425;
        color: white;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--borde);
        border-radius: 12px;
    }

    input, textarea {
        border-radius: 9px !important;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .marca {
            padding: 18px;
        }

        .marca h1 {
            font-size: 23px;
        }

        [data-testid="stMetric"] {
            padding: 10px;
        }

        [data-testid="stMetricValue"] {
            font-size: 22px;
        }

        [data-testid="stSidebar"] [data-testid="stButton"] button {
            min-height: 48px;
        }

        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. FUNCIONES GENERALES
# ============================================================

def hoy_peru():
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
    return str(valor).strip() if valor is not None else ""


def mostrar_marca():
    st.markdown(
        f"""
        <div class="marca">
            <h1>🍽️ {NOMBRE_APP}</h1>
            <p>Pedidos, ventas, menús y empresas</p>
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
    try:
        supabase.table("registro_sistema").insert({
            "nivel": str(nivel)[:30],
            "operacion": str(operacion)[:150],
            "detalle": str(detalle)[:4000],
        }).execute()
    except Exception:
        pass


def normalizar_platos(lista):
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
    if not texto:
        return []
    return normalizar_platos(re.split(r"[,;\n]+", str(texto)))


def leer_tabla(nombre_tabla, orden=None, descendente=False):
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

    return consulta.order("tipo").order("nombre").execute().data or []


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
    if not limpiar_texto(cliente):
        return "Escribe el nombre del cliente y vuelve a intentarlo."

    if precio < PRECIO_MINIMO or precio > PRECIO_MAXIMO:
        return (
            f"El precio por menú debe estar entre "
            f"{dinero(PRECIO_MINIMO)} y {dinero(PRECIO_MAXIMO)}."
        )

    if int(cantidad) < 1:
        return "La cantidad mínima es 1 menú."

    if int(cantidad) > 10000:
        return "La cantidad es demasiado grande."

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

    df["fecha"] = pd.to_datetime(
        df["fecha"], errors="coerce"
    ).dt.date

    df["cliente"] = df["cliente"].fillna("").astype(str)
    df["empresa"] = df["empresa"].fillna("").astype(str)

    for columna in ["precio_menu", "cantidad_menus", "total"]:
        df[columna] = pd.to_numeric(
            df[columna], errors="coerce"
        ).fillna(0)

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
    pedidos = int(len(df))
    menus = int(df["cantidad_menus"].sum())

    return {
        "ventas": ventas,
        "pedidos": pedidos,
        "menus": menus,
        "promedio": ventas / pedidos if pedidos else 0,
    }


def resumen_por_empresa(df):
    columnas = ["Empresa", "Ventas totales", "Pedidos", "Menús vendidos"]

    if df.empty:
        return pd.DataFrame(columns=columnas)

    temporal = df.copy()
    temporal["empresa"] = temporal["empresa"].str.strip()
    temporal["empresa"] = temporal["empresa"].replace("", "Sin empresa")

    resumen = (
        temporal.groupby("empresa", as_index=False)
        .agg(
            ventas=("total", "sum"),
            pedidos=("id", "count"),
            menus=("cantidad_menus", "sum"),
        )
        .sort_values("ventas", ascending=False)
        .rename(columns={
            "empresa": "Empresa",
            "ventas": "Ventas totales",
            "pedidos": "Pedidos",
            "menus": "Menús vendidos",
        })
    )

    resumen["Ventas totales"] = resumen["Ventas totales"].round(2)
    return resumen


def mostrar_resumen_empresas(df, titulo="Ventas por empresa"):
    st.subheader(titulo)

    if df.empty:
        st.info("No hay ventas registradas en este período.")
        return

    resumen = resumen_por_empresa(df)

    # Mostrar importes legibles en la tabla.
    tabla = resumen.copy()
    tabla["Ventas totales"] = tabla["Ventas totales"].apply(dinero)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇️ Descargar cuadro de ventas por empresa",
        data=resumen.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"ventas_empresas_{hoy_peru().isoformat()}.csv",
        mime="text/csv",
    )

    grafico = resumen.set_index("Empresa")["Ventas totales"]
    st.bar_chart(grafico)


# ============================================================
# 4. CONEXIÓN A SUPABASE
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
            "sin rutas adicionales."
        )

    supabase = create_client(URL_SUPABASE, CLAVE_SUPABASE)

except Exception as error:
    st.title("🍽️ Como en Casa Dely")
    mostrar_error(
        "No se pudo conectar con Supabase. Revisa los secretos de Streamlit.",
        error,
    )
    st.stop()


# ============================================================
# 5. ACCESO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"


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
            if contrasena and contrasena == str(st.secrets["APP_PASSWORD"]):
                st.session_state.autenticado = True
                registrar_evento("INFO", "Inicio de sesión", "Acceso correcto")
                st.rerun()
            else:
                st.error("La contraseña no es correcta.")
        except Exception as error:
            mostrar_error("No se encontró APP_PASSWORD en los secretos.", error)

    st.stop()


# ============================================================
# 6. NAVEGACIÓN
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
    st.caption(f"Fecha de Perú: {hoy_peru():%d/%m/%Y}")

    if st.button("🚪 Cerrar sesión", use_container_width=True):
        cerrar_sesion()


pagina = st.session_state.pagina


# ============================================================
# 7. CARGAR PEDIDOS
# ============================================================

try:
    pedidos = cargar_pedidos()
    df_pedidos = preparar_dataframe(pedidos)

except Exception as error:
    registrar_evento("ERROR", "Cargar pedidos", error)
    mostrar_error("No se pudieron cargar los pedidos.", error)
    st.stop()


# ============================================================
# 8. INICIO
# ============================================================

if pagina == "Inicio":
    mostrar_marca()
    st.subheader("Panel de control")

    hoy = hoy_peru()
    df_hoy = df_pedidos[df_pedidos["fecha"] == hoy].copy()

    ih = calcular_indicadores(df_hoy)
    it = calcular_indicadores(df_pedidos)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas de hoy", dinero(ih["ventas"]))
    c2.metric("Pedidos de hoy", ih["pedidos"])
    c3.metric("Menús de hoy", ih["menus"])

    empresas_hoy = df_hoy.loc[
        df_hoy["empresa"].str.strip() != "", "empresa"
    ].nunique()

    c4.metric("Empresas atendidas hoy", int(empresas_hoy))

    st.divider()
    st.subheader("Acumulado registrado")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Ventas acumuladas", dinero(it["ventas"]))
    a2.metric("Pedidos acumulados", it["pedidos"])
    a3.metric("Menús acumulados", it["menus"])
    a4.metric("Promedio por pedido", dinero(it["promedio"]))

    st.divider()

    if not df_pedidos.empty:
        mostrar_resumen_empresas(
            df_pedidos,
            "Cuadro general: cuánto vendemos a cada empresa",
        )

        st.divider()
        st.subheader("Ventas por día")

        por_dia = (
            df_pedidos.groupby("fecha", as_index=False)["total"]
            .sum()
            .sort_values("fecha")
            .tail(30)
        )

        por_dia["fecha"] = por_dia["fecha"].astype(str)
        st.bar_chart(por_dia.set_index("fecha")["total"])

        st.subheader("Pedidos recientes")

        recientes = df_pedidos.head(10).copy()
        recientes["fecha"] = recientes["fecha"].apply(texto_fecha)
        recientes["total"] = recientes["total"].apply(dinero)

        st.dataframe(
            recientes[
                ["id", "fecha", "cliente", "empresa", "cantidad_menus", "total"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Todavía no hay pedidos registrados.")


# ============================================================
# 9. REGISTRAR PEDIDO
# ============================================================

elif pagina == "Registrar pedido":
    mostrar_marca()
    st.subheader("Registrar nuevo pedido")

    try:
        catalogo_activo = cargar_catalogo(solo_activos=True)
    except Exception as error:
        registrar_evento("ERROR", "Leer catálogo", error)
        catalogo_activo = []
        st.warning("No se pudo cargar el catálogo. Puedes escribir los platos.")

    entradas_catalogo = sorted(set(
        f["nombre"] for f in catalogo_activo
        if f.get("tipo") == "Entrada"
    ))

    segundos_catalogo = sorted(set(
        f["nombre"] for f in catalogo_activo
        if f.get("tipo") == "Segundo"
    ))

    empresas_existentes = sorted(set(
        limpiar_texto(x)
        for x in df_pedidos["empresa"].tolist()
        if limpiar_texto(x)
    ))

    # Importante:
    # clear_on_submit=False evita borrar los campos tras enviar el formulario.
    # Cada widget tiene una clave estable para conservar su valor.
    with st.form("form_registrar_pedido", clear_on_submit=False):
        st.markdown("#### 🧾 Datos del pedido")

        c1, c2 = st.columns(2)

        with c1:
            fecha_pedido = st.date_input(
                "Fecha del pedido",
                value=hoy_peru(),
                key="nuevo_fecha",
            )

            st.text_input(
                "Nombre del cliente *",
                placeholder="Escribe el nombre del cliente",
                key="nuevo_cliente",
            )

            empresa_seleccion = st.selectbox(
                "Empresa",
                ["Sin empresa registrada"] + empresas_existentes + ["Otra empresa"],
                key="nuevo_empresa_seleccion",
            )

            if empresa_seleccion == "Otra empresa":
                st.text_input(
                    "Nombre de la nueva empresa",
                    key="nuevo_empresa_texto",
                )

        with c2:
            precio = st.number_input(
                "Precio por menú (S/)",
                min_value=PRECIO_MINIMO,
                max_value=PRECIO_MAXIMO,
                value=15.0,
                step=0.5,
                key="nuevo_precio",
            )

            cantidad = st.number_input(
                "Cantidad de menús",
                min_value=1,
                max_value=10000,
                value=1,
                step=1,
                key="nuevo_cantidad",
            )

            st.metric(
                "Total calculado",
                dinero(calcular_total(precio, cantidad)),
            )

        st.divider()
        st.markdown("#### 🍲 Menú")

        st.multiselect(
            "Entradas del catálogo",
            options=entradas_catalogo,
            key="nuevo_entradas",
        )

        st.text_area(
            "Otras entradas (opcional)",
            placeholder="Separa los platos con comas o saltos de línea",
            key="nuevo_entradas_extra",
        )

        st.multiselect(
            "Segundos del catálogo",
            options=segundos_catalogo,
            key="nuevo_segundos",
        )

        st.text_area(
            "Otros segundos (opcional)",
            placeholder="Separa los platos con comas o saltos de línea",
            key="nuevo_segundos_extra",
        )

        st.text_input(
            "Dirección de entrega",
            placeholder="Dirección completa",
            key="nuevo_direccion",
        )

        st.text_area(
            "Observaciones",
            placeholder="Indicaciones, cambios o comentarios",
            key="nuevo_observaciones",
        )

        guardar = st.form_submit_button(
            "💾 Guardar pedido",
            type="primary",
            use_container_width=True,
        )

    if guardar:
        # Leemos directamente los valores guardados en el estado de Streamlit.
        cliente = limpiar_texto(st.session_state.get("nuevo_cliente", ""))

        if empresa_seleccion == "Otra empresa":
            empresa = limpiar_texto(
                st.session_state.get("nuevo_empresa_texto", "")
            )
        elif empresa_seleccion == "Sin empresa registrada":
            empresa = ""
        else:
            empresa = empresa_seleccion

        direccion = limpiar_texto(
            st.session_state.get("nuevo_direccion", "")
        )
        observaciones = limpiar_texto(
            st.session_state.get("nuevo_observaciones", "")
        )

        error_validacion = validar_pedido(cliente, precio, cantidad)

        entradas_finales = normalizar_platos(
            st.session_state.get("nuevo_entradas", [])
            + separar_platos(st.session_state.get("nuevo_entradas_extra", ""))
        )

        segundos_finales = normalizar_platos(
            st.session_state.get("nuevo_segundos", [])
            + separar_platos(st.session_state.get("nuevo_segundos_extra", ""))
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

                if direccion:
                    nuevo_pedido["observaciones"] = (
                        f"Dirección: {direccion}\n{observaciones}".strip()
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
                    registrar_evento(
                        "ERROR",
                        "Guardar detalles del pedido",
                        f"Pedido {pedido_id}: {error_detalle}",
                    )

                    st.warning(
                        f"El pedido #{pedido_id} se guardó, pero hubo un "
                        "problema guardando los platos. Revísalo en Pedidos."
                    )
                else:
                    registrar_evento(
                        "INFO",
                        "Crear pedido",
                        f"Pedido #{pedido_id}; cliente={cliente}; total={total}",
                    )

                    st.success(
                        f"Pedido #{pedido_id} guardado correctamente. "
                        f"Total: {dinero(total)}"
                    )

                # Solo limpiamos los campos después de guardar correctamente.
                for clave in [
                    "nuevo_cliente",
                    "nuevo_empresa_texto",
                    "nuevo_direccion",
                    "nuevo_observaciones",
                    "nuevo_entradas_extra",
                    "nuevo_segundos_extra",
                ]:
                    st.session_state[clave] = ""

                for clave in ["nuevo_entradas", "nuevo_segundos"]:
                    st.session_state[clave] = []

                st.rerun()

            except Exception as error:
                registrar_evento("ERROR", "Crear pedido", error)

                mostrar_error(
                    "No se pudo confirmar el registro. Antes de volver a "
                    "guardar, revisa Pedidos para comprobar si el pedido "
                    "ya se creó y evitar duplicarlo.",
                    error,
                )


# ============================================================
# 10. HISTORIAL, EDICIÓN Y ELIMINACIÓN
# ============================================================

elif pagina == "Pedidos":
    mostrar_marca()
    st.subheader("Historial de pedidos")

    if df_pedidos.empty:
        st.info("No hay pedidos registrados.")
    else:
        with st.expander("🔎 Buscar y filtrar", expanded=True):
            fecha_minima = min(df_pedidos["fecha"].dropna())
            fecha_maxima = max(df_pedidos["fecha"].dropna())

            f1, f2 = st.columns(2)

            with f1:
                rango = st.date_input(
                    "Rango de fechas",
                    value=(fecha_minima, fecha_maxima),
                    key="hist_rango",
                )

            with f2:
                filtro_cliente = st.text_input(
                    "Buscar cliente",
                    key="hist_cliente",
                )

                empresas = sorted(set(
                    x for x in df_pedidos["empresa"].tolist() if x
                ))

                filtro_empresa = st.selectbox(
                    "Empresa",
                    ["Todas"] + empresas,
                    key="hist_empresa",
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

        indicadores = calcular_indicadores(df_filtrado)
        m1, m2, m3 = st.columns(3)
        m1.metric("Ventas filtradas", dinero(indicadores["ventas"]))
        m2.metric("Pedidos encontrados", indicadores["pedidos"])
        m3.metric("Menús vendidos", indicadores["menus"])

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
            "⬇️ Exportar pedidos a CSV",
            data=df_filtrado.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"pedidos_{hoy_peru().isoformat()}.csv",
            mime="text/csv",
        )

        st.divider()
        st.subheader("Editar o eliminar un pedido")

        ids = df_filtrado["id"].tolist()

        if ids:
            id_seleccionado = st.selectbox(
                "Selecciona un pedido",
                ids,
                format_func=lambda x: (
                    f"Pedido #{x} — "
                    f"{df_filtrado.loc[df_filtrado['id'] == x, 'cliente'].iloc[0]}"
                ),
            )

            pedido_actual = next(
                p for p in pedidos if p.get("id") == id_seleccionado
            )

            detalles_actuales = []

            try:
                detalles_actuales = cargar_detalles([id_seleccionado])
            except Exception as error:
                mostrar_error("No se pudieron leer los platos del pedido.", error)

            entradas_actuales = normalizar_platos([
                d.get("plato", "") for d in detalles_actuales
                if d.get("tipo") == "Entrada"
            ])

            segundos_actuales = normalizar_platos([
                d.get("plato", "") for d in detalles_actuales
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

            with st.expander("✏️ Editar pedido"):
                with st.form(f"editar_{id_seleccionado}"):
                    ec1, ec2 = st.columns(2)

                    with ec1:
                        e_fecha = st.date_input(
                            "Fecha",
                            value=pd.to_datetime(
                                pedido_actual.get("fecha")
                            ).date(),
                        )

                        e_cliente = st.text_input(
                            "Cliente",
                            value=pedido_actual.get("cliente", ""),
                        )

                        e_empresa = st.text_input(
                            "Empresa",
                            value=pedido_actual.get("empresa", "") or "",
                        )

                    with ec2:
                        e_precio = st.number_input(
                            "Precio por menú",
                            min_value=PRECIO_MINIMO,
                            max_value=PRECIO_MAXIMO,
                            value=float(pedido_actual.get("precio_menu") or 15),
                            step=0.5,
                        )

                        e_cantidad = st.number_input(
                            "Cantidad de menús",
                            min_value=1,
                            max_value=10000,
                            value=max(
                                1,
                                int(pedido_actual.get("cantidad_menus") or 1),
                            ),
                        )

                    e_entradas = st.multiselect(
                        "Entradas",
                        opciones_entradas,
                        default=entradas_actuales,
                    )

                    e_segundos = st.multiselect(
                        "Segundos",
                        opciones_segundos,
                        default=segundos_actuales,
                    )

                    e_observaciones = st.text_area(
                        "Observaciones",
                        value=pedido_actual.get("observaciones", "") or "",
                    )

                    st.metric(
                        "Nuevo total",
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
                            (
                                supabase.table("pedidos")
                                .update({
                                    "fecha": e_fecha.isoformat(),
                                    "cliente": limpiar_texto(e_cliente),
                                    "empresa": limpiar_texto(e_empresa),
                                    "precio_menu": float(e_precio),
                                    "cantidad_menus": int(e_cantidad),
                                    "total": calcular_total(e_precio, e_cantidad),
                                    "observaciones": limpiar_texto(e_observaciones),
                                })
                                .eq("id", id_seleccionado)
                                .execute()
                            )

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
                                "Revisa el pedido antes de volver a intentarlo.",
                                error,
                            )

            with st.expander("🗑️ Eliminar pedido"):
                st.warning(
                    "Se eliminarán el pedido y sus platos asociados. "
                    "Esta acción no se puede deshacer."
                )

                confirmar = st.checkbox(
                    f"Confirmo eliminar el pedido #{id_seleccionado}",
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
                        mostrar_error("No se pudo eliminar el pedido.", error)


# ============================================================
# 11. ESTADÍSTICAS
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
            mostrar_resumen_empresas(
                df_periodo,
                "Ventas por empresa en el período elegido",
            )

            if not df_periodo.empty:
                st.divider()
                st.subheader("Resumen por día")

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

                st.subheader("Ventas por cliente")

                por_cliente = (
                    df_periodo.groupby("cliente", as_index=False)
                    .agg(
                        ventas=("total", "sum"),
                        pedidos=("id", "count"),
                        menus=("cantidad_menus", "sum"),
                    )
                    .sort_values("ventas", ascending=False)
                )

                por_cliente["ventas"] = por_cliente["ventas"].round(2)

                st.dataframe(
                    por_cliente,
                    use_container_width=True,
                    hide_index=True,
                )

            st.download_button(
                "⬇️ Descargar pedidos del período",
                data=df_periodo.to_csv(index=False).encode("utf-8-sig"),
                file_name=(
                    f"resumen_{fecha_inicio.isoformat()}_"
                    f"{fecha_fin.isoformat()}.csv"
                ),
                mime="text/csv",
            )


# ============================================================
# 12. CATÁLOGO DE PLATOS
# ============================================================

elif pagina == "Catálogo":
    mostrar_marca()
    st.subheader("Catálogo de entradas y segundos")

    st.markdown(
        '<div class="nota">Los platos inactivos dejan de aparecer '
        'en nuevos pedidos, pero se conservan en el historial.</div>',
        unsafe_allow_html=True,
    )

    try:
        catalogo = cargar_catalogo(solo_activos=False)
    except Exception as error:
        mostrar_error("No se pudo abrir el catálogo.", error)
        st.stop()

    with st.expander("➕ Agregar plato", expanded=True):
        with st.form("form_nuevo_plato"):
            tipo_nuevo = st.selectbox("Tipo", ["Entrada", "Segundo"])
            nombre_nuevo = st.text_input("Nombre del plato")
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
                existe = any(
                    f.get("tipo") == tipo_nuevo
                    and limpiar_texto(f.get("nombre")).casefold()
                    == nombre_nuevo.casefold()
                    for f in catalogo
                )

                if existe:
                    st.warning("Ese plato ya existe en ese tipo.")
                else:
                    try:
                        supabase.table("catalogo_platos").insert({
                            "tipo": tipo_nuevo,
                            "nombre": nombre_nuevo,
                            "activo": True,
                        }).execute()

                        registrar_evento(
                            "INFO", "Crear plato",
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
        st.info("El catálogo está vacío.")
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

        ids_catalogo = [f["id"] for f in catalogo]

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
                "Tipo",
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
                "Guardar cambios",
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
                        "INFO", "Editar plato",
                        f"Plato #{id_plato}: {nombre_editar}",
                    )

                    st.success("Catálogo actualizado.")
                    st.rerun()

                except Exception as error:
                    registrar_evento("ERROR", "Editar plato", error)
                    mostrar_error(
                        "No se pudo actualizar. Comprueba si ya existe "
                        "otro plato con el mismo nombre y tipo.",
                        error,
                    )


# ============================================================
# 13. EMPRESAS
# ============================================================

elif pagina == "Empresas":
    mostrar_marca()
    st.subheader("Ventas por empresa")

    st.write(
        "Consulta cuánto has vendido a cada empresa, cuántos pedidos "
        "ha realizado y cuántos menús has vendido."
    )

    if df_pedidos.empty:
        st.info("Todavía no hay pedidos para agrupar por empresa.")
    else:
        f1, f2 = st.columns(2)

        with f1:
            fecha_minima = min(df_pedidos["fecha"].dropna())
            fecha_maxima = max(df_pedidos["fecha"].dropna())

            fecha_inicio = st.date_input(
                "Desde",
                value=fecha_minima,
                key="emp_inicio",
            )

        with f2:
            fecha_fin = st.date_input(
                "Hasta",
                value=fecha_maxima,
                key="emp_fin",
            )

        if fecha_inicio > fecha_fin:
            st.error("La fecha inicial no puede ser posterior a la final.")
        else:
            df_empresas = filtrar_por_fechas(
                df_pedidos, fecha_inicio, fecha_fin
            )

            indicadores = calcular_indicadores(df_empresas)

            a1, a2, a3 = st.columns(3)
            a1.metric("Ventas del período", dinero(indicadores["ventas"]))
            a2.metric("Pedidos", indicadores["pedidos"])
            a3.metric("Menús vendidos", indicadores["menus"])

            mostrar_resumen_empresas(
                df_empresas,
                "Cuadro de ventas por empresa",
            )

    st.divider()
    st.subheader("Corregir el nombre de una empresa")

    empresas_existentes = sorted(set(
        limpiar_texto(x)
        for x in df_pedidos["empresa"].tolist()
        if limpiar_texto(x)
    ))

    if not empresas_existentes:
        st.info("Todavía no hay empresas registradas.")
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
                    f"Vas a cambiar {empresa_antigua!r} por "
                    f"{empresa_nueva!r} en todos sus pedidos."
                )

                confirmar_empresa = st.checkbox(
                    "Confirmo el cambio de nombre",
                    key="confirmar_empresa_global",
                )

                if confirmar_empresa and st.button(
                    "Aplicar cambio",
                    type="primary",
                    key="aplicar_cambio_empresa",
                ):
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

                        st.success("Nombre de empresa actualizado.")
                        st.rerun()

                    except Exception as error:
                        registrar_evento("ERROR", "Renombrar empresa", error)
                        mostrar_error(
                            "No se pudo actualizar el nombre de la empresa.",
                            error,
                        )


# ============================================================
# 14. SISTEMA
# ============================================================

elif pagina == "Sistema":
    mostrar_marca()
    st.subheader("Estado del sistema")

    st.metric("Versión", VERSION_APP)
    st.metric("Pedidos registrados", len(df_pedidos))

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

            columnas = [
                c for c in ["fecha", "nivel", "operacion", "detalle"]
                if c in df_eventos.columns
            ]

            st.dataframe(
                df_eventos[columnas].head(200),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Todavía no hay eventos registrados.")

    except Exception as error:
        mostrar_error("No se pudo leer el registro de eventos.", error)

    st.divider()
    st.subheader("Comprobar tablas")

    if st.button("Comprobar acceso a las tablas", type="primary"):
        for tabla in [
            "pedidos",
            "detalle_pedido",
            "catalogo_platos",
            "registro_sistema",
        ]:
            try:
                supabase.table(tabla).select("*").limit(1).execute()
                st.success(f"{tabla}: correcto")
            except Exception as error:
                st.error(f"{tabla}: error — {error}")


# ============================================================
# 15. PIE DE PÁGINA
# ============================================================

st.divider()
st.caption(
    f"{NOMBRE_APP} · Versión {VERSION_APP} · "
    "Gestión de pedidos y ventas"
)
