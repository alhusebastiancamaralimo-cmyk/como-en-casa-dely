
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

CREMA = "#FAF4E8"
MARFIL = "#FFFDF8"
MARRON = "#4A3025"
MARRON_CLARO = "#72503D"
CARAMELO = "#C28A52"
TEXTO = "#33271F"
SECUNDARIO = "#87776A"
BORDE = "#E9DDCD"
VERDE = "#397653"


# =====================================================
# ESTILO
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --crema: #FAF4E8;
    --marfil: #FFFDF8;
    --marron: #4A3025;
    --marron-claro: #72503D;
    --caramelo: #C28A52;
    --texto: #33271F;
    --secundario: #87776A;
    --borde: #E9DDCD;
}

.stApp {
    background: var(--crema);
    color: var(--texto);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(250,244,232,0.95);
}

[data-testid="stSidebar"] {
    background: var(--marfil);
    border-right: 1px solid var(--borde);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 0.9rem;
}

h1, h2, h3 {
    color: var(--marron) !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: -0.5px;
}

h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
}

h2 {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}

p, label, input, textarea {
    font-family: 'DM Sans', sans-serif;
}

.brand {
    background: linear-gradient(145deg, #4A3025, #72503D);
    border-radius: 20px;
    padding: 21px 17px;
    margin-bottom: 22px;
    box-shadow: 0 8px 22px rgba(74,48,37,0.13);
    color: white;
}

.brand-icon {
    font-size: 32px;
    margin-bottom: 9px;
}

.brand-name {
    color: white;
    font-size: 21px;
    font-weight: 700;
    line-height: 1.25;
}

.brand-sub {
    color: #EBD4B9;
    font-size: 10px;
    letter-spacing: 1.4px;
    margin-top: 8px;
    text-transform: uppercase;
}

.nav-caption {
    color: #9B8978;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.7px;
    margin: 22px 0 10px 5px;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 43px;
    font-weight: 600;
    transition: all 0.18s ease;
}

[data-testid="stSidebar"] div.stButton > button {
    text-align: left;
    padding-left: 15px;
    background: transparent;
    color: var(--marron);
    border: 1px solid transparent;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background: #F4EADD;
    border-color: #E6D5C1;
    color: var(--marron);
}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: var(--marron);
    color: white;
    border: 1px solid var(--marron);
    box-shadow: 0 5px 12px rgba(74,48,37,0.12);
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button {
    background: var(--marron);
    color: white;
    border: 1px solid var(--marron);
    border-radius: 12px;
    min-height: 45px;
    font-weight: 700;
}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    background: var(--marron-claro);
    color: white;
    border-color: var(--marron-claro);
}

.stButton > button:not([kind="primary"]) {
    background: var(--marfil);
    color: var(--marron);
    border: 1px solid var(--borde);
}

.stButton > button:not([kind="primary"]):hover {
    background: #F4EADD;
    color: var(--marron);
}

div[data-testid="stMetric"] {
    background: var(--marfil);
    border: 1px solid var(--borde);
    border-radius: 17px;
    padding: 20px;
    box-shadow: 0 5px 16px rgba(74,48,37,0.035);
}

div[data-testid="stMetricLabel"] {
    color: var(--secundario);
    font-size: 13px;
}

div[data-testid="stMetricValue"] {
    color: var(--marron);
    font-weight: 700;
}

div[data-testid="stForm"] {
    background: var(--marfil);
    border: 1px solid var(--borde);
    border-radius: 19px;
    padding: 23px;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background: white;
    border-radius: 10px;
    border-color: #DFD0BE;
}

div[data-baseweb="select"] > div {
    border-radius: 10px;
    border-color: #DFD0BE;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--borde);
    border-radius: 13px;
    overflow: hidden;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: var(--borde);
}

.hero {
    background: linear-gradient(120deg, #4A3025, #72503D);
    border-radius: 23px;
    padding: 30px;
    color: white;
    margin: 4px 0 24px 0;
    box-shadow: 0 10px 25px rgba(74,48,37,0.12);
}

.hero-tag {
    color: #E8C59D;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    color: white;
    font-size: 29px;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 9px;
}

.hero-text {
    color: #F0E1D2;
    font-size: 14px;
    line-height: 1.7;
}

.section-caption {
    color: var(--secundario);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 24px 0 12px 0;
    text-transform: uppercase;
}

.sidebar-footer {
    background: #F4EADD;
    border-radius: 13px;
    padding: 13px;
    margin-top: 12px;
    color: var(--marron);
    font-size: 12px;
}

@media (max-width: 700px) {
    .hero {
        padding: 22px;
        border-radius: 17px;
    }
    .hero-title {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# FUNCIONES GENERALES
# =====================================================

def hoy_peru():
    return datetime.now(ZoneInfo("America/Lima")).date()


def dinero(valor):
    return f"S/ {float(valor or 0):,.2f}"


def mostrar_marca():
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🍗</div>
        <div class="brand-name">Como en Casa Dely</div>
        <div class="brand-sub">Sabor casero · Gestión de ventas</div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_error(titulo, error):
    st.error(titulo)
    with st.expander("🔎 Ver detalles técnicos", expanded=True):
        st.code(f"{type(error).__name__}: {error}", language="text")
        st.caption(
            "Antes de compartir este error, revisa que no contenga "
            "contraseñas, claves API ni tokens."
        )


# =====================================================
# INICIO DE SESIÓN
# =====================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if not st.session_state.autenticado:
    _, centro, _ = st.columns([1, 1.1, 1])

    with centro:
        st.write("")
        st.write("")
        mostrar_marca()

        st.title("Bienvenido")
        st.write("Ingresa tu contraseña para acceder a tu negocio.")

        with st.form("login"):
            clave = st.text_input(
                "Contraseña de acceso",
                type="password",
                placeholder="Escribe tu contraseña"
            )
            ingresar = st.form_submit_button(
                "Entrar al sistema →",
                use_container_width=True
            )

        if ingresar:
            try:
                if clave == st.secrets["APP_PASSWORD"]:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("La contraseña es incorrecta.")
            except Exception:
                st.error(
                    "No se encontró APP_PASSWORD en los Secrets de Streamlit."
                )

        st.caption("Sistema privado · Como en Casa Dely")

    st.stop()


# =====================================================
# SUPABASE
# =====================================================

@st.cache_resource
def conectar_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


try:
    db = conectar_supabase()
except Exception as error:
    st.title("Como en Casa Dely")
    mostrar_error("No se pudo conectar con Supabase.", error)
    st.stop()


# =====================================================
# OPERACIONES DE PEDIDOS
# =====================================================

def guardar_pedido(
    fecha_pedido,
    cliente,
    empresa,
    precio,
    cantidad,
    observaciones,
    entradas,
    segundos
):
    total = round(float(precio) * int(cantidad), 2)

    respuesta = db.table("pedidos").insert({
        "fecha": fecha_pedido.isoformat(),
        "cliente": cliente.strip(),
        "empresa": empresa.strip() or None,
        "precio_menu": float(precio),
        "cantidad_menus": int(cantidad),
        "total": total,
        "observaciones": observaciones.strip() or None
    }).execute()

    if not respuesta.data:
        raise RuntimeError(
            "Supabase no devolvió el pedido creado."
        )

    pedido_id = respuesta.data[0]["id"]

    detalles = []

    for tipo, texto in [
        ("Entrada", entradas),
        ("Segundo", segundos)
    ]:
        for plato in texto.split(","):
            plato = plato.strip()
            if plato:
                detalles.append({
                    "pedido_id": pedido_id,
                    "tipo": tipo,
                    "plato": plato,
                    "cantidad": 1
                })

    if detalles:
        db.table("detalle_pedido").insert(detalles).execute()

    return pedido_id, total


def obtener_pedidos(limite=500):
    respuesta = (
        db.table("pedidos")
        .select("*")
        .order("fecha", desc=True)
        .order("id", desc=True)
        .limit(limite)
        .execute()
    )
    return respuesta.data or []


# =====================================================
# MENÚ LATERAL CON BOTONES
# =====================================================

with st.sidebar:
    mostrar_marca()

    st.markdown(
        '<div class="nav-caption">MENÚ PRINCIPAL</div>',
        unsafe_allow_html=True
    )

    opciones = [
        ("Inicio", "⌂", "Inicio"),
        ("Registrar pedido", "＋", "Registrar pedido"),
        ("Pedidos", "▤", "Historial de pedidos"),
        ("Estadísticas", "▥", "Estadísticas")
    ]

    for clave_pagina, icono, etiqueta in opciones:
        seleccionado = st.session_state.pagina == clave_pagina

        if st.button(
            f"{icono}    {etiqueta}",
            key=f"nav_{clave_pagina}",
            type="primary" if seleccionado else "secondary",
            use_container_width=True
        ):
            st.session_state.pagina = clave_pagina
            st.rerun()

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-footer">
        <strong>● Sistema de ventas</strong><br>
        <span style="color:#87776A">Acceso privado</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if st.button(
        "↪  Cerrar sesión",
        key="cerrar_sesion",
        use_container_width=True
    ):
        st.session_state.autenticado = False
        st.session_state.pagina = "Inicio"
        st.rerun()


# =====================================================
# INICIO
# =====================================================

if st.session_state.pagina == "Inicio":
    hoy = hoy_peru()

    st.markdown(f"""
    <div class="hero">
        <div class="hero-tag">TU NEGOCIO, MÁS ORGANIZADO</div>
        <div class="hero-title">¡Hola! Bienvenido a tu panel 👋</div>
        <div class="hero-text">
            Controla tus pedidos y ventas desde un solo lugar.
            Que no se te escape ningún detalle.
        </div>
        <div style="margin-top:15px;color:#E8C59D;font-size:12px">
            📅 {hoy.strftime("%d/%m/%Y")} · COMO EN CASA DELY
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Resumen de hoy")

    try:
        pedidos = obtener_pedidos()

        pedidos_hoy = [
            p for p in pedidos
            if str(p.get("fecha", ""))[:10] == hoy.isoformat()
        ]

        ventas_hoy = sum(
            float(p.get("total") or 0) for p in pedidos_hoy
        )

        menus_hoy = sum(
            int(p.get("cantidad_menus") or 0) for p in pedidos_hoy
        )

        a, b, c = st.columns(3)
        a.metric("💰 Ventas de hoy", dinero(ventas_hoy))
        b.metric("▤ Pedidos de hoy", len(pedidos_hoy))
        c.metric("🍽️ Menús vendidos", menus_hoy)

        st.markdown(
            '<div class="section-caption">ACCESOS RÁPIDOS</div>',
            unsafe_allow_html=True
        )

        a, b = st.columns(2)

        with a:
            st.markdown("#### ＋ Registrar una venta")
            st.write("Agrega un pedido y calcula su total.")
            if st.button(
                "Nuevo pedido →",
                key="nuevo_inicio",
                type="primary",
                use_container_width=True
            ):
                st.session_state.pagina = "Registrar pedido"
                st.rerun()

        with b:
            st.markdown("#### ▤ Historial")
            st.write("Consulta los pedidos guardados.")
            if st.button(
                "Ver pedidos →",
                key="ver_inicio",
                use_container_width=True
            ):
                st.session_state.pagina = "Pedidos"
                st.rerun()

        st.markdown(
            '<div class="section-caption">ÚLTIMOS PEDIDOS</div>',
            unsafe_allow_html=True
        )

        if pedidos:
            columnas = [
                "id", "fecha", "cliente",
                "cantidad_menus", "total"
            ]
            datos = [
                {k: p.get(k) for k in columnas}
                for p in pedidos[:5]
            ]

            st.dataframe(
                datos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("N.º"),
                    "fecha": st.column_config.TextColumn("Fecha"),
                    "cliente": st.column_config.TextColumn("Cliente"),
                    "cantidad_menus": st.column_config.NumberColumn(
                        "Menús", format="%d"
                    ),
                    "total": st.column_config.NumberColumn(
                        "Total", format="S/ %.2f"
                    )
                }
            )
        else:
            st.info(
                "Todavía no hay pedidos registrados. "
                "Cuando guardes el primero, aparecerá aquí."
            )

    except Exception as error:
        mostrar_error("No se pudo cargar el inicio.", error)


# =====================================================
# REGISTRAR PEDIDO
# =====================================================

elif st.session_state.pagina == "Registrar pedido":
    st.title("Registrar pedido")
    st.write(
        "Introduce los datos de la venta. "
        "El importe se calcula automáticamente."
    )

    st.markdown(
        '<div class="section-caption">INFORMACIÓN DEL CLIENTE</div>',
        unsafe_allow_html=True
    )

    with st.form("formulario_pedido", clear_on_submit=False):
        a, b = st.columns(2)

        with a:
            cliente = st.text_input(
                "Nombre del cliente *",
                placeholder="Ej. María Pérez"
            )
            empresa = st.text_input(
                "Empresa (opcional)",
                placeholder="Nombre de la empresa"
            )

        with b:
            fecha_pedido = st.date_input(
                "Fecha del pedido",
                value=hoy_peru(),
                format="DD/MM/YYYY"
            )
            precio = st.number_input(
                "Precio por menú (S/)",
                min_value=10.0,
                max_value=20.0,
                value=15.0,
                step=0.5,
                format="%.2f"
            )
            cantidad = st.number_input(
                "Cantidad de menús",
                min_value=1,
                max_value=10000,
                value=1,
                step=1
            )

        st.markdown(
            '<div class="section-caption">DETALLES DEL MENÚ</div>',
            unsafe_allow_html=True
        )

        a, b = st.columns(2)

        with a:
            entradas = st.text_input(
                "Entradas",
                placeholder="Ej. Sopa, papa a la huancaína"
            )

        with b:
            segundos = st.text_input(
                "Segundos",
                placeholder="Ej. Arroz con pollo, ají de gallina"
            )

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Dirección, indicaciones u otros detalles..."
        )

        total = float(precio) * int(cantidad)

        st.markdown("---")
        a, b = st.columns([1, 1])

        with a:
            st.markdown("**TOTAL DEL PEDIDO**")
            st.markdown(
                f"<h2 style='color:{MARRON}'>{dinero(total)}</h2>",
                unsafe_allow_html=True
            )

        with b:
            st.write("")
            guardar = st.form_submit_button(
                "💾 Guardar pedido",
                use_container_width=True
            )

    if guardar:
        if not cliente.strip():
            st.error("Escribe el nombre del cliente.")
        else:
            try:
                pedido_id, total_guardado = guardar_pedido(
                    fecha_pedido,
                    cliente,
                    empresa,
                    precio,
                    cantidad,
                    observaciones,
                    entradas,
                    segundos
                )

                st.success(
                    f"¡Pedido #{pedido_id} guardado! "
                    f"Total: {dinero(total_guardado)}"
                )
                st.balloons()

            except Exception as error:
                mostrar_error("No se pudo completar el registro.", error)
                st.warning(
                    "Si falló el guardado de los detalles, "
                    "el pedido principal podría haberse guardado. "
                    "Comprueba el historial antes de volver a intentarlo."
                )


# =====================================================
# HISTORIAL
# =====================================================

elif st.session_state.pagina == "Pedidos":
    st.title("Historial de pedidos")
    st.write("Todos tus pedidos registrados, organizados en un solo lugar.")

    try:
        pedidos = obtener_pedidos()

        if not pedidos:
            st.info("Todavía no hay pedidos guardados.")
        else:
            filtro = st.text_input(
                "🔎 Buscar cliente o empresa",
                placeholder="Escribe un nombre..."
            )

            filtrados = pedidos

            if filtro.strip():
                texto = filtro.strip().casefold()
                filtrados = [
                    p for p in pedidos
                    if texto in str(p.get("cliente") or "").casefold()
                    or texto in str(p.get("empresa") or "").casefold()
                ]

            st.caption(
                f"{len(filtrados)} pedido(s) encontrados. "
                "Se consultan hasta 500 registros recientes."
            )

            columnas = [
                "id", "fecha", "cliente", "empresa",
                "precio_menu", "cantidad_menus",
                "total", "observaciones"
            ]

            datos = [
                {k: p.get(k) for k in columnas}
                for p in filtrados
            ]

            st.dataframe(
                datos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("N.º"),
                    "fecha": st.column_config.TextColumn("Fecha"),
                    "cliente": st.column_config.TextColumn("Cliente"),
                    "empresa": st.column_config.TextColumn("Empresa"),
                    "precio_menu": st.column_config.NumberColumn(
                        "Precio/menú", format="S/ %.2f"
                    ),
                    "cantidad_menus": st.column_config.NumberColumn(
                        "Cantidad", format="%d"
                    ),
                    "total": st.column_config.NumberColumn(
                        "Total", format="S/ %.2f"
                    ),
                    "observaciones": st.column_config.TextColumn(
                        "Observaciones", width="large"
                    )
                }
            )

    except Exception as error:
        mostrar_error("No se pudieron consultar los pedidos.", error)


# =====================================================
# ESTADÍSTICAS
# =====================================================

elif st.session_state.pagina == "Estadísticas":
    st.title("Estadísticas")
    st.write("Consulta el rendimiento de las ventas del día.")

    try:
        pedidos = obtener_pedidos()
        hoy = hoy_peru().isoformat()

        pedidos_hoy = [
            p for p in pedidos
            if str(p.get("fecha", ""))[:10] == hoy
        ]

        ventas = sum(
            float(p.get("total") or 0) for p in pedidos_hoy
        )
        menus = sum(
            int(p.get("cantidad_menus") or 0) for p in pedidos_hoy
        )
        promedio = ventas / len(pedidos_hoy) if pedidos_hoy else 0

        a, b = st.columns(2)
        c, d = st.columns(2)

        a.metric("💰 Ventas de hoy", dinero(ventas))
        b.metric("▤ Pedidos de hoy", len(pedidos_hoy))
        c.metric("🍽️ Menús vendidos", menus)
        d.metric("🧾 Promedio por pedido", dinero(promedio))

        st.markdown(
            '<div class="section-caption">DETALLE DE VENTAS DE HOY</div>',
            unsafe_allow_html=True
        )

        if pedidos_hoy:
            datos = [
                {
                    "Pedido": p.get("id"),
                    "Cliente": p.get("cliente"),
                    "Menús": p.get("cantidad_menus"),
                    "Total": float(p.get("total") or 0)
                }
                for p in pedidos_hoy
            ]

            st.dataframe(
                datos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total": st.column_config.NumberColumn(
                        "Total", format="S/ %.2f"
                    ),
                    "Menús": st.column_config.NumberColumn(
                        "Menús", format="%d"
                    )
                }
            )
        else:
            st.info("Todavía no hay ventas registradas para hoy.")

        st.caption(
            "El resumen utiliza hasta 500 pedidos recientes."
        )

    except Exception as error:
        mostrar_error("No se pudieron calcular las estadísticas.", error)
