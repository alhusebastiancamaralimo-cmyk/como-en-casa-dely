import io
import re
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from supabase import create_client

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded",
)

VERSION = "5.2.0"

# =========================================================
# DISEÑO VISUAL
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --fondo: #F5F0E7;
    --blanco: #FFFCF7;
    --cafe: #493628;
    --cafe-oscuro: #211911;
    --nogal: #302218;
    --crema: #E8DCC8;
    --arena: #D6C4A8;
    --texto: #352A20;
    --suave: #897C6E;
    --verde: #547A61;
    --borde: #E5DCCF;
    --acento: #CBB697;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--fondo);
    color: var(--texto);
}

[data-testid="stHeader"] {
    background: rgba(245,240,231,.96);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* BARRA LATERAL DE MADERA */

[data-testid="stSidebar"] {
    background-color: #261B13;
    background-image:
        linear-gradient(
            90deg,
            rgba(10,6,3,.38) 0%,
            rgba(90,62,39,.13) 20%,
            rgba(12,7,4,.30) 43%,
            rgba(91,62,39,.12) 66%,
            rgba(9,6,4,.38) 100%
        ),
        repeating-linear-gradient(
            88deg,
            transparent 0px,
            rgba(0,0,0,.13) 3px,
            transparent 7px,
            rgba(207,169,126,.055) 12px,
            transparent 20px,
            rgba(0,0,0,.17) 31px,
            transparent 42px
        ),
        repeating-linear-gradient(
            2deg,
            rgba(0,0,0,.09) 0px,
            transparent 2px,
            rgba(194,154,110,.04) 4px,
            transparent 8px
        ),
        linear-gradient(180deg, #493323 0%, #2D2016 48%, #1F160F 100%);
    border-right: 1px solid rgba(232,220,200,.12);
    box-shadow: 5px 0 22px rgba(25,16,9,.08);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.3rem;
}

[data-testid="stSidebar"] * {
    color: #F5EBDD;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #CBBBA5;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(232,220,200,.18);
    margin: 1.1rem 0;
}

.marca-lateral {
    padding: 17px 14px 19px;
    border: 1px solid rgba(232,220,200,.15);
    border-radius: 16px;
    background: linear-gradient(
        145deg,
        rgba(255,248,235,.09),
        rgba(0,0,0,.16)
    );
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
    text-align: center;
}

.marca-icono {
    font-size: 2.5rem;
    margin-bottom: 6px;
    filter: drop-shadow(0 3px 3px rgba(0,0,0,.3));
}

.marca-nombre {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.22rem;
    line-height: 1.35;
    font-weight: 700;
    color: #FFF7E9;
}

.marca-descripcion {
    margin-top: 7px;
    color: #CBBBA5;
    font-size: .74rem;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex;
    align-items: center;
    padding: 10px 12px;
    border-radius: 11px;
    border: 1px solid transparent;
    background: rgba(255,255,255,0);
    transition: background .2s ease, border-color .2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(245,231,210,.09);
    border-color: rgba(232,220,200,.10);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(
        110deg,
        rgba(222,204,174,.22),
        rgba(222,204,174,.08)
    );
    border: 1px solid rgba(222,204,174,.30);
    box-shadow: inset 3px 0 0 #D9C6A7;
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: #FFF7E9;
    font-weight: 700;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    font-size: .91rem;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #B7A48E;
    font-size: .76rem;
}

[data-testid="stSidebar"] div.stButton > button {
    color: #F6EBDD;
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(232,220,200,.20);
    border-radius: 10px;
    min-height: 42px;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(232,220,200,.13);
    border-color: #CBB697;
    color: #FFF7E9;
}

/* ENCABEZADOS */

h1, h2, h3 {
    color: var(--cafe-oscuro);
    font-family: 'Playfair Display', Georgia, serif;
}

h1 {
    font-size: 2.15rem !important;
    letter-spacing: -.5px;
}

h2 {
    font-size: 1.55rem !important;
}

h3 {
    font-size: 1.2rem !important;
}

.marca {
    background:
        linear-gradient(110deg, rgba(24,17,11,.97), rgba(69,49,31,.97)),
        repeating-linear-gradient(90deg, #302218, #4A3423 12px, #302218 25px);
    border: 1px solid rgba(203,182,151,.18);
    border-radius: 20px;
    padding: 25px 30px;
    margin-bottom: 25px;
    color: #FFF8F0;
    box-shadow: 0 8px 24px rgba(56,37,28,.13);
    position: relative;
    overflow: hidden;
}

.marca:after {
    content: "✦";
    position: absolute;
    right: 34px;
    top: -28px;
    font-size: 130px;
    color: rgba(255,255,255,.06);
}

.marca h1 {
    color: #FFF8F0 !important;
    font-size: 2rem !important;
    margin: 0 0 5px 0;
}

.marca p {
    color: #DCCDB9 !important;
    margin: 0;
    font-size: .95rem;
}

.etiqueta {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 30px;
    background: rgba(232,220,200,.13);
    border: 1px solid rgba(232,220,200,.12);
    color: #E8DCC8;
    font-size: .75rem;
    margin-bottom: 12px;
    letter-spacing: .8px;
}

/* TARJETAS Y PANELES */

.tarjeta {
    background: var(--blanco);
    border: 1px solid var(--borde);
    border-radius: 17px;
    padding: 20px;
    min-height: 140px;
    box-shadow: 0 3px 12px rgba(56,37,28,.035);
}

.tarjeta .icono {
    font-size: 1.5rem;
    margin-bottom: 12px;
}

.tarjeta .titulo {
    font-size: .85rem;
    color: var(--suave);
    margin-bottom: 7px;
    font-weight: 600;
}

.tarjeta .valor {
    color: var(--cafe-oscuro);
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.25;
}

.tarjeta .detalle {
    color: var(--suave);
    font-size: .78rem;
    margin-top: 7px;
}

.panel {
    background: var(--blanco);
    border: 1px solid var(--borde);
    border-radius: 17px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(56,37,28,.035);
}

.panel-titulo {
    font-family: 'Playfair Display', Georgia, serif;
    color: var(--cafe-oscuro);
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.panel-subtitulo {
    color: var(--suave);
    font-size: .84rem;
    margin-bottom: 17px;
}

div[data-testid="stMetric"] {
    background: var(--blanco);
    border: 1px solid var(--borde);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 3px 12px rgba(56,37,28,.035);
}

[data-testid="stMetricLabel"] {
    color: var(--suave);
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--cafe-oscuro);
    font-weight: 700;
}

/* BOTONES Y FORMULARIOS */

div.stButton > button,
div.stDownloadButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    border-color: var(--borde);
    color: var(--cafe);
    transition: all .2s ease;
}

div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: var(--cafe);
    color: white;
    border-color: var(--cafe);
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    border-color: #9C8769;
    color: #6C563E;
}

div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button[kind="primary"]:hover {
    background: #2D2117;
    color: white;
    border-color: #2D2117;
}

div[data-testid="stForm"] {
    background: var(--blanco);
    border: 1px solid var(--borde);
    border-radius: 16px;
    padding: 22px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--borde);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 9px;
}

[data-testid="stSelectbox"] > div > div {
    border-radius: 9px;
}

hr {
    border-color: var(--borde);
}

.stAlert {
    border-radius: 12px;
}

a {
    color: #6C563E;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem .8rem 2rem .8rem;
    }

    .marca {
        padding: 20px;
        border-radius: 15px;
    }

    .marca h1 {
        font-size: 1.65rem !important;
    }

    .tarjeta {
        padding: 14px;
        min-height: 125px;
    }

    .tarjeta .valor {
        font-size: 1.4rem;
    }

    .panel {
        padding: 15px;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# CONEXIÓN
# =========================================================

def secreto(nombre, defecto=""):
    try:
        return str(st.secrets.get(nombre, defecto)).strip()
    except Exception:
        return defecto


URL = secreto("SUPABASE_URL")
KEY = secreto("SUPABASE_KEY")
PASSWORD = secreto("APP_PASSWORD")

if not URL or not KEY:
    st.error("Falta SUPABASE_URL o SUPABASE_KEY en los secretos de Streamlit.")
    st.stop()

try:
    db = create_client(URL, KEY)
except Exception as e:
    st.error(f"No se pudo conectar con Supabase: {e}")
    st.stop()


# =========================================================
# FUNCIONES GENERALES
# =========================================================

def error_ui(e, accion):
    st.error(f"No se pudo {accion}. Comprueba la conexión y los permisos.")
    with st.expander("Detalles técnicos"):
        st.code(str(e))


def leer(tabla, columnas="*"):
    resultado = []
    inicio = 0

    while True:
        respuesta = (
            db.table(tabla)
            .select(columnas)
            .range(inicio, inicio + 999)
            .execute()
        )
        filas = respuesta.data or []
        resultado.extend(filas)

        if len(filas) < 1000:
            break

        inicio += 1000

    return resultado


def registrar_evento(operacion, detalle="", nivel="INFO"):
    try:
        db.table("registro_sistema").insert({
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "nivel": nivel,
            "operacion": operacion,
            "detalle": str(detalle)[:2000],
        }).execute()
    except Exception:
        pass


def dinero(valor):
    try:
        return f"S/ {float(valor or 0):,.2f}"
    except (ValueError, TypeError):
        return "S/ 0.00"


def limpio(valor):
    return re.sub(r"\s+", " ", str(valor or "")).strip()


def fecha_segura(valor):
    try:
        resultado = pd.to_datetime(valor, errors="coerce")
        if pd.isna(resultado):
            return None
        return resultado.date()
    except Exception:
        return None


def direccion_y_notas(texto):
    direccion = ""
    notas = []

    for linea in str(texto or "").splitlines():
        m = re.match(r"^\s*Dirección:\s*(.*)$", linea, re.I)
        if m and not direccion:
            direccion = m.group(1).strip()
        else:
            notas.append(linea)

    return direccion, "\n".join(notas).strip()


def observaciones_finales(direccion, notas):
    direccion = limpio(direccion)
    notas = str(notas or "").strip()
    notas = re.sub(
        r"(?im)^\s*Dirección:\s*.*(?:\n|$)",
        "",
        notas,
    ).strip()

    return (
        f"Dirección: {direccion}\n{notas}".strip()
        if direccion else notas
    )


@st.cache_data(ttl=20, show_spinner=False)
def pedidos_cargar():
    datos = leer("pedidos")
    return sorted(datos, key=lambda x: str(x.get("fecha") or ""), reverse=True)


@st.cache_data(ttl=20, show_spinner=False)
def detalles_cargar():
    return leer("detalle_pedido")


@st.cache_data(ttl=30, show_spinner=False)
def empresas_cargar():
    return leer("empresas")


@st.cache_data(ttl=30, show_spinner=False)
def catalogo_cargar():
    return leer("catalogo_platos")


def refrescar():
    pedidos_cargar.clear()
    detalles_cargar.clear()
    empresas_cargar.clear()
    catalogo_cargar.clear()


def exportar(datos, nombre):
    if not datos:
        st.info("No hay datos para exportar.")
        return

    df = pd.DataFrame(datos)
    izq, der = st.columns(2)

    with izq:
        st.download_button(
            "📄 Descargar CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{nombre}_{date.today().isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with der:
        try:
            buffer = io.BytesIO()

            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Datos")

            st.download_button(
                "📊 Descargar Excel",
                buffer.getvalue(),
                file_name=f"{nombre}_{date.today().isoformat()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception:
            st.caption("Para Excel, instala openpyxl en requirements.txt.")


def banner(titulo, subtitulo):
    st.markdown(
        f'<div class="marca">'
        f'<div class="etiqueta">COMO EN CASA DELY · ADMINISTRACIÓN</div>'
        f'<h1>{titulo}</h1><p>{subtitulo}</p></div>',
        unsafe_allow_html=True,
    )


def tarjeta(icono, titulo, valor, detalle=""):
    st.markdown(
        f'<div class="tarjeta"><div class="icono">{icono}</div>'
        f'<div class="titulo">{titulo}</div>'
        f'<div class="valor">{valor}</div>'
        f'<div class="detalle">{detalle}</div></div>',
        unsafe_allow_html=True,
    )


def panel_titulo(titulo, subtitulo=""):
    st.markdown(
        f'<div class="panel-titulo">{titulo}</div>'
        f'<div class="panel-subtitulo">{subtitulo}</div>',
        unsafe_allow_html=True,
    )


def esta_activo(registro):
    # Los registros antiguos sin campo "activo" se consideran activos.
    return bool(registro.get("activo", True))


def actualizar_direccion_empresa():
    """Completa la dirección cuando se selecciona una empresa."""
    seleccion = st.session_state.get("empresa_pedido", "Sin empresa")

    if seleccion == "Sin empresa":
        st.session_state["direccion_pedido"] = ""
        return

    try:
        empresas = empresas_cargar()
        empresa = next(
            (
                e for e in empresas
                if limpio(e.get("nombre")) == limpio(seleccion)
            ),
            None,
        )

        if empresa:
            st.session_state["direccion_pedido"] = str(
                empresa.get("direccion") or ""
            )
    except Exception:
        pass


def cambiar_estado_plato(plato):
    """Activa o desactiva un plato sin borrarlo."""
    nuevo_estado = not esta_activo(plato)

    db.table("catalogo_platos").update({
        "activo": nuevo_estado,
    }).eq("id", plato["id"]).execute()

    estado_texto = "activado" if nuevo_estado else "desactivado"

    registrar_evento(
        "CAMBIAR_ESTADO_PLATO",
        f"{plato.get('nombre', '')}: {estado_texto}",
    )

    refrescar()


# =========================================================
# ACCESO
# =========================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = not bool(PASSWORD)

if PASSWORD and not st.session_state.autenticado:
    banner("Bienvenido", "Ingresa para administrar tus pedidos y ventas.")

    with st.form("acceso"):
        clave = st.text_input("Contraseña", type="password")
        entrar = st.form_submit_button("Ingresar", type="primary")

    if entrar:
        if clave == PASSWORD:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")

    st.stop()


# =========================================================
# NAVEGACIÓN IZQUIERDA
# =========================================================

PAGINAS = [
    "🏠  Inicio",
    "📝  Registrar pedido",
    "🧾  Pedidos",
    "📊  Estadísticas",
    "🏢  Empresas",
    "🍽️  Catálogo",
    "⚙️  Sistema",
]

MAPA_PAGINAS = {
    "🏠  Inicio": "Inicio",
    "📝  Registrar pedido": "Registrar pedido",
    "🧾  Pedidos": "Pedidos",
    "📊  Estadísticas": "Estadísticas",
    "🏢  Empresas": "Empresas",
    "🍽️  Catálogo": "Catálogo",
    "⚙️  Sistema": "Sistema",
}

INVERSO_PAGINAS = {v: k for k, v in MAPA_PAGINAS.items()}

with st.sidebar:
    st.markdown("""
    <div class="marca-lateral">
        <div class="marca-icono">🍗</div>
        <div class="marca-nombre">Como en Casa Dely</div>
        <div class="marca-descripcion">Panel de administración</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.caption("MENÚ PRINCIPAL")

    pagina_anterior = st.session_state.get("pagina", "Inicio")
    opcion_anterior = INVERSO_PAGINAS.get(pagina_anterior, PAGINAS[0])

    opcion = st.radio(
        "NAVEGACIÓN",
        PAGINAS,
        index=PAGINAS.index(opcion_anterior),
        label_visibility="collapsed",
        key="navegacion_lateral",
    )

    pagina = MAPA_PAGINAS[opcion]
    st.session_state.pagina = pagina

    st.divider()
    st.caption("GESTIÓN DEL NEGOCIO")
    st.caption(f"Versión {VERSION}")

    if st.button("↻  Actualizar datos", use_container_width=True):
        refrescar()
        st.rerun()

    if PASSWORD and st.button("⇥  Cerrar sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()


# =========================================================
# INICIO / DASHBOARD
# =========================================================

if pagina == "Inicio":
    banner(
        "Resumen de tu negocio",
        "Todo lo importante de Como en Casa Dely, de un vistazo.",
    )

    try:
        pedidos = pedidos_cargar()
        empresas = empresas_cargar()

        hoy = date.today()
        mes_actual = hoy.month
        anio_actual = hoy.year

        pedidos_hoy = [
            p for p in pedidos if fecha_segura(p.get("fecha")) == hoy
        ]

        pedidos_mes = [
            p for p in pedidos
            if fecha_segura(p.get("fecha"))
            and fecha_segura(p.get("fecha")).month == mes_actual
            and fecha_segura(p.get("fecha")).year == anio_actual
        ]

        venta_hoy = sum(float(p.get("total") or 0) for p in pedidos_hoy)
        venta_mes = sum(float(p.get("total") or 0) for p in pedidos_mes)
        menus_hoy = sum(int(p.get("cantidad_menus") or 0) for p in pedidos_hoy)
        activas = sum(1 for e in empresas if esta_activo(e))

        st.markdown("### ✨ Hoy en tu negocio")
        a, b, c, d = st.columns(4)

        with a:
            tarjeta("💰", "VENTAS DE HOY", dinero(venta_hoy),
                    f"{len(pedidos_hoy)} pedidos registrados")
        with b:
            tarjeta("🍱", "MENÚS VENDIDOS", f"{menus_hoy:,}",
                    "Unidades de hoy")
        with c:
            tarjeta("📈", "VENTAS DEL MES", dinero(venta_mes),
                    hoy.strftime("%B %Y").capitalize())
        with d:
            tarjeta("🏢", "EMPRESAS ACTIVAS", str(activas),
                    "Clientes empresariales")

        st.write("")
        izquierda, derecha = st.columns([1.6, 1])

        with izquierda:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo(
                "📊 Evolución de ventas",
                "Ingresos diarios de los últimos 14 días",
            )

            desde = hoy - timedelta(days=13)
            por_dia = {}

            for p in pedidos:
                f = fecha_segura(p.get("fecha"))
                if f and desde <= f <= hoy:
                    clave = f.strftime("%d %b")
                    por_dia[clave] = (
                        por_dia.get(clave, 0) + float(p.get("total") or 0)
                    )

            fechas = [desde + timedelta(days=i) for i in range(14)]
            datos_grafico = []

            for f in fechas:
                clave = f.strftime("%d %b")
                datos_grafico.append({
                    "Día": clave,
                    "Ventas": por_dia.get(clave, 0),
                })

            st.line_chart(
                pd.DataFrame(datos_grafico).set_index("Día"),
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with derecha:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo(
                "🏆 Empresas principales",
                "Según las ventas de este mes",
            )

            ventas_empresa = {}
            for p in pedidos_mes:
                nombre = limpio(p.get("empresa")) or "Sin empresa"
                ventas_empresa[nombre] = (
                    ventas_empresa.get(nombre, 0) + float(p.get("total") or 0)
                )

            top = sorted(
                ventas_empresa.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5]

            if top:
                for i, (nombre, valor) in enumerate(top, 1):
                    st.markdown(
                        f"**{i}. {nombre}**  \n"
                        f"<span style='color:#79664E;font-size:1.1rem;font-weight:700'>"
                        f"{dinero(valor)}</span>",
                        unsafe_allow_html=True,
                    )
                    st.divider()
            else:
                st.info("Todavía no hay ventas este mes.")

            st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_titulo("🧾 Pedidos recientes", "Los últimos movimientos de tu negocio")

        if pedidos:
            filas = []
            for p in pedidos[:8]:
                filas.append({
                    "N.º": p.get("id", ""),
                    "Fecha": p.get("fecha", ""),
                    "Cliente": p.get("cliente", ""),
                    "Empresa": p.get("empresa", "") or "Particular",
                    "Menús": p.get("cantidad_menus", 0),
                    "Total": dinero(p.get("total", 0)),
                })

            st.dataframe(
                pd.DataFrame(filas),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Tu actividad aparecerá aquí cuando registres el primer pedido.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("### ⚡ Accesos rápidos")
        x, y, z = st.columns(3)

        with x:
            if st.button("＋ Registrar pedido", use_container_width=True):
                st.session_state.pagina = "Registrar pedido"
                st.rerun()

        with y:
            if st.button("▦ Ver todos los pedidos", use_container_width=True):
                st.session_state.pagina = "Pedidos"
                st.rerun()

        with z:
            if st.button("＋ Agregar empresa", use_container_width=True):
                st.session_state.pagina = "Empresas"
                st.rerun()

    except Exception as e:
        error_ui(e, "cargar el dashboard")


# =========================================================
# REGISTRAR PEDIDO
# AUTOCOMPLETADO DE CLIENTES, EMPRESAS Y PLATOS
# =========================================================

elif pagina == "Registrar pedido":
    banner(
        "Nuevo pedido",
        "Busca datos anteriores, completa los detalles y guarda el pedido.",
    )

    if st.session_state.pop("limpiar_pedido", False):
        for k in [
            "cliente", "empresa_pedido", "direccion_pedido", "precio",
            "cantidad", "entrada", "segundo", "bebida", "notas",
            "fecha_pedido",
        ]:
            st.session_state.pop(k, None)

    try:
        pedidos_existentes = pedidos_cargar()
        empresas = [
            e for e in empresas_cargar()
            if esta_activo(e)
        ]
        catalogo = catalogo_cargar()

        clientes_existentes = sorted({
            limpio(p.get("cliente"))
            for p in pedidos_existentes
            if limpio(p.get("cliente"))
        }, key=str.casefold)

        opciones_empresas = ["Sin empresa"] + sorted({
            limpio(e.get("nombre"))
            for e in empresas
            if limpio(e.get("nombre"))
        }, key=str.casefold)

        platos_activos = [
            p for p in catalogo
            if esta_activo(p)
        ]

        entradas = sorted({
            limpio(p.get("nombre"))
            for p in platos_activos
            if limpio(p.get("nombre"))
            and str(p.get("tipo", "")).casefold() == "entrada"
        }, key=str.casefold)

        segundos = sorted({
            limpio(p.get("nombre"))
            for p in platos_activos
            if limpio(p.get("nombre"))
            and str(p.get("tipo", "")).casefold() == "segundo"
        }, key=str.casefold)

        bebidas = sorted({
            limpio(p.get("nombre"))
            for p in platos_activos
            if limpio(p.get("nombre"))
            and str(p.get("tipo", "")).casefold()
            in {"bebida", "extra", "otro"}
        }, key=str.casefold)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### 👤 Datos del cliente")
        st.caption(
            "Empieza a escribir para encontrar datos anteriores. "
            "También puedes registrar un nombre nuevo."
        )

        # Se usa selectbox con opciones nuevas para permitir
        # tanto buscar clientes existentes como escribir uno nuevo.
        cliente = st.selectbox(
            "Nombre del cliente *",
            options=clientes_existentes,
            index=None,
            placeholder="Escribe o busca el nombre del cliente...",
            accept_new_options=True,
            key="cliente",
        )

        c1, c2 = st.columns(2)

        with c1:
            empresa = st.selectbox(
                "Empresa",
                options=opciones_empresas,
                key="empresa_pedido",
                on_change=actualizar_direccion_empresa,
            )

            direccion = st.text_input(
                "Dirección de entrega",
                key="direccion_pedido",
                placeholder="Se completa al elegir una empresa",
            )

        with c2:
            fecha_pedido = st.date_input(
                "Fecha del pedido",
                value=date.today(),
                key="fecha_pedido",
            )

            precio = st.number_input(
                "Precio por menú (S/)",
                min_value=0.0,
                value=15.0,
                step=0.5,
                key="precio",
            )

            cantidad = st.number_input(
                "Cantidad de menús",
                min_value=1,
                max_value=10000,
                value=1,
                step=1,
                key="cantidad",
            )

        empresa_elegida = next(
            (
                e for e in empresas
                if limpio(e.get("nombre")) == limpio(empresa)
            ),
            None,
        )

        if empresa_elegida:
            contacto = limpio(empresa_elegida.get("contacto"))
            telefono = limpio(empresa_elegida.get("telefono"))

            datos_contacto = []
            if contacto:
                datos_contacto.append(f"Contacto: {contacto}")
            if telefono:
                datos_contacto.append(f"Teléfono: {telefono}")

            if datos_contacto:
                st.caption(" · ".join(datos_contacto))

        st.divider()
        st.markdown("### 🍽️ Detalles de la comida")
        st.caption(
            "Las sugerencias provienen de los platos activos del catálogo. "
            "Puedes escribir un plato nuevo si todavía no lo registraste."
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            entrada = st.selectbox(
                "Entrada",
                options=entradas,
                index=None,
                placeholder="Buscar o escribir entrada...",
                accept_new_options=True,
                key="entrada",
            )

        with c2:
            segundo = st.selectbox(
                "Segundo",
                options=segundos,
                index=None,
                placeholder="Buscar o escribir segundo...",
                accept_new_options=True,
                key="segundo",
            )

        with c3:
            bebida = st.selectbox(
                "Bebida o adicional",
                options=bebidas,
                index=None,
                placeholder="Buscar o escribir bebida...",
                accept_new_options=True,
                key="bebida",
            )

        notas = st.text_area(
            "Observaciones",
            key="notas",
            placeholder="Indicaciones especiales, referencias u otros detalles...",
        )

        total = float(precio) * int(cantidad)

        st.info(f"**Total del pedido: {dinero(total)}**")

        guardar = st.button(
            "💾 Guardar pedido",
            type="primary",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if guardar:
            nombre_cliente = limpio(cliente)

            if not nombre_cliente:
                st.error("Escribe el nombre del cliente.")
            elif precio <= 0:
                st.error("El precio debe ser mayor que cero.")
            else:
                registro = {
                    "fecha": fecha_pedido.isoformat(),
                    "cliente": nombre_cliente,
                    "empresa": "" if empresa == "Sin empresa" else limpio(empresa),
                    "precio_menu": float(precio),
                    "cantidad_menus": int(cantidad),
                    "total": round(total, 2),
                    "observaciones": observaciones_finales(direccion, notas),
                }

                try:
                    respuesta = db.table("pedidos").insert(registro).execute()

                    if not respuesta.data:
                        raise RuntimeError("Supabase no devolvió el pedido creado.")

                    pedido_id = respuesta.data[0].get("id")

                    if pedido_id is None:
                        raise RuntimeError("No se recibió el ID del pedido.")

                    detalles = []

                    for tipo, plato in [
                        ("Entrada", entrada),
                        ("Segundo", segundo),
                        ("Bebida/Adicional", bebida),
                    ]:
                        if limpio(plato):
                            detalles.append({
                                "pedido_id": pedido_id,
                                "tipo": tipo,
                                "plato": limpio(plato),
                                "cantidad": int(cantidad),
                            })

                    if detalles:
                        try:
                            db.table("detalle_pedido").insert(detalles).execute()
                        except Exception as detalle_error:
                            try:
                                db.table("pedidos").delete().eq(
                                    "id", pedido_id
                                ).execute()
                            except Exception:
                                pass

                            raise RuntimeError(
                                "Falló el guardado de los detalles. "
                                "Se intentó cancelar el pedido. "
                                f"Detalle: {detalle_error}"
                            )

                    registrar_evento(
                        "CREAR_PEDIDO",
                        f"Pedido {pedido_id}",
                    )

                    refrescar()
                    st.session_state.limpiar_pedido = True
                    st.success(
                        f"Pedido #{pedido_id} registrado por {dinero(total)}."
                    )
                    st.rerun()

                except Exception as e:
                    error_ui(e, "guardar el pedido")

    except Exception as e:
        error_ui(e, "cargar los datos para el pedido")


# =========================================================
# PEDIDOS: HISTORIAL, EDICIÓN Y ELIMINACIÓN
# =========================================================

elif pagina == "Pedidos":
    banner("Pedidos", "Consulta, busca, edita y exporta los pedidos.")

    try:
        pedidos = pedidos_cargar()

        if not pedidos:
            st.info("Todavía no hay pedidos registrados.")
        else:
            busqueda = st.text_input("🔎 Buscar por cliente, empresa o ID")
            a, b = st.columns(2)

            with a:
                desde = st.date_input(
                    "Desde",
                    date.today() - timedelta(days=30),
                    key="pedidos_desde",
                )

            with b:
                hasta = st.date_input(
                    "Hasta",
                    date.today(),
                    key="pedidos_hasta",
                )

            if desde > hasta:
                st.error("La fecha inicial no puede ser posterior a la final.")
                st.stop()

            filtrados = []

            for p in pedidos:
                f = fecha_segura(p.get("fecha"))

                if f and not desde <= f <= hasta:
                    continue

                texto = " ".join([
                    str(p.get("id", "")),
                    str(p.get("cliente", "")),
                    str(p.get("empresa", "")),
                ]).lower()

                if busqueda and busqueda.lower() not in texto:
                    continue

                filtrados.append(p)

            filas = []

            for p in filtrados:
                direccion, notas = direccion_y_notas(
                    p.get("observaciones", "")
                )

                filas.append({
                    "ID": p.get("id"),
                    "Fecha": p.get("fecha", ""),
                    "Cliente": p.get("cliente", ""),
                    "Empresa": p.get("empresa", "") or "Particular",
                    "Menús": p.get("cantidad_menus", 0),
                    "Precio": dinero(p.get("precio_menu", 0)),
                    "Total": dinero(p.get("total", 0)),
                    "Dirección": direccion,
                    "Observaciones": notas,
                })

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo("Historial", f"{len(filtrados)} pedidos encontrados")
            st.dataframe(
                pd.DataFrame(filas),
                use_container_width=True,
                hide_index=True,
            )
            exportar(filas, "pedidos")
            st.markdown('</div>', unsafe_allow_html=True)

            ids = [
                p.get("id") for p in filtrados
                if p.get("id") is not None
            ]

            if ids:
                st.write("")
                st.markdown("### Administrar pedido")

                pid = st.selectbox(
                    "Selecciona un pedido",
                    ids,
                    format_func=lambda x: f"Pedido #{x} — " + next(
                        (
                            str(p.get("cliente", ""))
                            for p in filtrados
                            if str(p.get("id")) == str(x)
                        ),
                        "",
                    ),
                )

                p = next(
                    p for p in filtrados
                    if str(p.get("id")) == str(pid)
                )

                direccion_actual, notas_actuales = direccion_y_notas(
                    p.get("observaciones", "")
                )

                with st.expander("✏️ Editar datos"):
                    with st.form("editar_pedido"):
                        cliente_editar = st.text_input(
                            "Cliente",
                            value=str(p.get("cliente", "")),
                        )
                        empresa_editar = st.text_input(
                            "Empresa",
                            value=str(p.get("empresa", "")),
                        )
                        direccion_editar = st.text_input(
                            "Dirección",
                            value=direccion_actual,
                        )

                        fecha_actual = fecha_segura(p.get("fecha")) or date.today()

                        fecha_editar = st.date_input(
                            "Fecha",
                            value=fecha_actual,
                        )

                        precio_editar = st.number_input(
                            "Precio por menú",
                            min_value=0.0,
                            value=float(p.get("precio_menu") or 0),
                            step=0.5,
                        )

                        cantidad_editar = st.number_input(
                            "Cantidad de menús",
                            min_value=1,
                            max_value=10000,
                            value=max(1, int(p.get("cantidad_menus") or 1)),
                        )

                        notas_editar = st.text_area(
                            "Observaciones",
                            value=notas_actuales,
                        )

                        actualizar = st.form_submit_button(
                            "Guardar cambios",
                            type="primary",
                        )

                    if actualizar:
                        if not limpio(cliente_editar):
                            st.error("El cliente no puede quedar vacío.")
                        elif precio_editar <= 0:
                            st.error("El precio debe ser mayor que cero.")
                        else:
                            try:
                                db.table("pedidos").update({
                                    "fecha": fecha_editar.isoformat(),
                                    "cliente": limpio(cliente_editar),
                                    "empresa": limpio(empresa_editar),
                                    "precio_menu": float(precio_editar),
                                    "cantidad_menus": int(cantidad_editar),
                                    "total": round(
                                        float(precio_editar)
                                        * int(cantidad_editar), 2
                                    ),
                                    "observaciones": observaciones_finales(
                                        direccion_editar,
                                        notas_editar,
                                    ),
                                }).eq("id", pid).execute()

                                registrar_evento(
                                    "EDITAR_PEDIDO",
                                    f"Pedido {pid}",
                                )
                                refrescar()
                                st.success("Pedido actualizado.")
                                st.rerun()

                            except Exception as e:
                                error_ui(e, "actualizar el pedido")

                with st.expander("🗑️ Eliminar pedido"):
                    st.warning(
                        "Se eliminará el pedido y sus detalles. "
                        "Esta acción no se puede deshacer."
                    )

                    confirmar = st.checkbox(
                        "Confirmo que quiero eliminarlo",
                        key=f"confirmar_{pid}",
                    )

                    if st.button(
                        "Eliminar pedido",
                        disabled=not confirmar,
                        type="primary",
                    ):
                        try:
                            db.table("detalle_pedido").delete().eq(
                                "pedido_id", pid
                            ).execute()

                            db.table("pedidos").delete().eq(
                                "id", pid
                            ).execute()

                            registrar_evento(
                                "ELIMINAR_PEDIDO",
                                f"Pedido {pid}",
                                "AVISO",
                            )
                            refrescar()
                            st.success("Pedido eliminado.")
                            st.rerun()

                        except Exception as e:
                            error_ui(e, "eliminar el pedido")

    except Exception as e:
        error_ui(e, "cargar los pedidos")


# =========================================================
# ESTADÍSTICAS
# =========================================================

elif pagina == "Estadísticas":
    banner(
        "Estadísticas",
        "Entiende tus ventas y toma mejores decisiones.",
    )

    try:
        pedidos = pedidos_cargar()
        fechas = [fecha_segura(p.get("fecha")) for p in pedidos]
        fechas = [f for f in fechas if f]

        if not fechas:
            st.info("Cuando registres pedidos, aquí aparecerán tus estadísticas.")
        else:
            a, b = st.columns(2)

            with a:
                desde = st.date_input(
                    "Desde",
                    value=max(
                        min(fechas),
                        date.today() - timedelta(days=30),
                    ),
                    min_value=min(fechas),
                    max_value=max(fechas),
                    key="estad_desde",
                )

            with b:
                hasta = st.date_input(
                    "Hasta",
                    value=max(fechas),
                    min_value=min(fechas),
                    max_value=max(fechas),
                    key="estad_hasta",
                )

            if desde > hasta:
                st.error("Revisa el rango de fechas.")
                st.stop()

            datos = [
                p for p in pedidos
                if fecha_segura(p.get("fecha"))
                and desde <= fecha_segura(p.get("fecha")) <= hasta
            ]

            venta = sum(float(p.get("total") or 0) for p in datos)
            menus = sum(int(p.get("cantidad_menus") or 0) for p in datos)

            x, y, z = st.columns(3)
            x.metric("Ventas totales", dinero(venta))
            y.metric("Pedidos", len(datos))
            z.metric("Menús vendidos", menus)

            st.write("")
            izq, der = st.columns(2)

            with izq:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                panel_titulo("Ventas por empresa")
                por_empresa = {}

                for p in datos:
                    nombre = limpio(p.get("empresa")) or "Particular"
                    por_empresa[nombre] = (
                        por_empresa.get(nombre, 0)
                        + float(p.get("total") or 0)
                    )

                if por_empresa:
                    df = pd.DataFrame([
                        {"Empresa": k, "Ventas": v}
                        for k, v in sorted(
                            por_empresa.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    ])
                    st.bar_chart(df.set_index("Empresa"))
                else:
                    st.info("Sin datos.")

                st.markdown('</div>', unsafe_allow_html=True)

            with der:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                panel_titulo("Ventas por día")
                por_dia = {}

                for p in datos:
                    f = fecha_segura(p.get("fecha"))
                    if f:
                        clave = f.isoformat()
                        por_dia[clave] = (
                            por_dia.get(clave, 0)
                            + float(p.get("total") or 0)
                        )

                if por_dia:
                    df = pd.DataFrame([
                        {"Fecha": k, "Ventas": v}
                        for k, v in sorted(por_dia.items())
                    ])
                    st.line_chart(df.set_index("Fecha"))
                else:
                    st.info("Sin datos.")

                st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            exportar(datos, "estadisticas")

    except Exception as e:
        error_ui(e, "calcular las estadísticas")


# =========================================================
# EMPRESAS
# =========================================================

elif pagina == "Empresas":
    banner(
        "Empresas",
        "Administra tus clientes empresariales de forma independiente.",
    )

    try:
        empresas = empresas_cargar()

        with st.expander(
            "＋ Registrar empresa",
            expanded=not bool(empresas),
        ):
            with st.form("crear_empresa"):
                nombre = st.text_input("Nombre de empresa *")
                contacto = st.text_input("Persona de contacto")
                telefono = st.text_input("Teléfono")
                direccion = st.text_input("Dirección")
                notas = st.text_area("Observaciones")

                guardar = st.form_submit_button(
                    "Guardar empresa",
                    type="primary",
                )

            if guardar:
                nombre = limpio(nombre)

                if not nombre:
                    st.error("Escribe el nombre de la empresa.")
                elif any(
                    limpio(e.get("nombre")).casefold() == nombre.casefold()
                    for e in empresas
                ):
                    st.error("Ya existe una empresa con ese nombre.")
                else:
                    try:
                        db.table("empresas").insert({
                            "nombre": nombre,
                            "contacto": limpio(contacto),
                            "telefono": limpio(telefono),
                            "direccion": limpio(direccion),
                            "observaciones": notas,
                            "activo": True,
                        }).execute()

                        registrar_evento("CREAR_EMPRESA", nombre)
                        refrescar()
                        st.success("Empresa registrada.")
                        st.rerun()

                    except Exception as e:
                        error_ui(e, "crear la empresa")

        empresas = empresas_cargar()

        if empresas:
            tabla = [{
                "ID": e.get("id"),
                "Empresa": e.get("nombre", ""),
                "Contacto": e.get("contacto", ""),
                "Teléfono": e.get("telefono", ""),
                "Dirección": e.get("direccion", ""),
                "Estado": "Activa" if esta_activo(e) else "Inactiva",
            } for e in empresas]

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo(
                "Directorio de empresas",
                f"{len(empresas)} empresas registradas",
            )
            st.dataframe(
                pd.DataFrame(tabla),
                use_container_width=True,
                hide_index=True,
            )
            exportar(tabla, "empresas")
            st.markdown('</div>', unsafe_allow_html=True)

            ids = [
                e.get("id") for e in empresas
                if e.get("id") is not None
            ]

            st.write("")
            st.markdown("### Editar empresa")

            eid = st.selectbox(
                "Selecciona una empresa",
                ids,
                format_func=lambda x: f"#{x} — " + next(
                    (
                        str(e.get("nombre", ""))
                        for e in empresas
                        if str(e.get("id")) == str(x)
                    ),
                    "",
                ),
            )

            e = next(
                e for e in empresas
                if str(e.get("id")) == str(eid)
            )

            with st.form("editar_empresa"):
                nombre_editar = st.text_input(
                    "Nombre",
                    value=str(e.get("nombre", "")),
                )
                contacto_editar = st.text_input(
                    "Contacto",
                    value=str(e.get("contacto", "")),
                )
                telefono_editar = st.text_input(
                    "Teléfono",
                    value=str(e.get("telefono", "")),
                )
                direccion_editar = st.text_input(
                    "Dirección",
                    value=str(e.get("direccion", "")),
                )
                notas_editar = st.text_area(
                    "Observaciones",
                    value=str(e.get("observaciones", "")),
                )
                activo_editar = st.checkbox(
                    "Empresa activa",
                    value=esta_activo(e),
                )

                actualizar = st.form_submit_button(
                    "Guardar cambios",
                    type="primary",
                )

            if actualizar:
                nombre_nuevo = limpio(nombre_editar)

                duplicada = any(
                    str(otra.get("id")) != str(eid)
                    and limpio(otra.get("nombre")).casefold()
                    == nombre_nuevo.casefold()
                    for otra in empresas
                )

                if not nombre_nuevo:
                    st.error("El nombre no puede estar vacío.")
                elif duplicada:
                    st.error("Ya existe otra empresa con ese nombre.")
                else:
                    try:
                        anterior = limpio(e.get("nombre"))

                        db.table("empresas").update({
                            "nombre": nombre_nuevo,
                            "contacto": limpio(contacto_editar),
                            "telefono": limpio(telefono_editar),
                            "direccion": limpio(direccion_editar),
                            "observaciones": notas_editar,
                            "activo": activo_editar,
                        }).eq("id", eid).execute()

                        if anterior != nombre_nuevo:
                            db.table("pedidos").update({
                                "empresa": nombre_nuevo
                            }).eq("empresa", anterior).execute()

                        registrar_evento("EDITAR_EMPRESA", nombre_nuevo)
                        refrescar()
                        st.success("Empresa actualizada.")
                        st.rerun()

                    except Exception as e:
                        error_ui(e, "actualizar la empresa")

        else:
            st.info("Todavía no hay empresas. Puedes registrar la primera arriba.")

    except Exception as e:
        error_ui(e, "cargar las empresas")


# =========================================================
# CATÁLOGO
# ACTIVAR Y DESACTIVAR PLATOS DIRECTAMENTE
# =========================================================

elif pagina == "Catálogo":
    banner(
        "Catálogo de platos",
        "Agrega platos y cambia su estado sin eliminarlos.",
    )

    try:
        catalogo = catalogo_cargar()

        with st.expander(
            "＋ Agregar plato",
            expanded=not bool(catalogo),
        ):
            with st.form("crear_plato"):
                nombre_nuevo = st.text_input("Nombre del plato *")
                tipo_nuevo = st.selectbox(
                    "Categoría",
                    ["Entrada", "Segundo", "Bebida", "Extra", "Otro"],
                )

                guardar_plato = st.form_submit_button(
                    "Guardar plato",
                    type="primary",
                )

            if guardar_plato:
                nombre_nuevo = limpio(nombre_nuevo)

                if not nombre_nuevo:
                    st.error("Escribe el nombre del plato.")
                elif any(
                    limpio(p.get("nombre")).casefold() == nombre_nuevo.casefold()
                    and str(p.get("tipo", "")).casefold()
                    == tipo_nuevo.casefold()
                    for p in catalogo
                ):
                    st.error("Ese plato ya existe en esa categoría.")
                else:
                    try:
                        db.table("catalogo_platos").insert({
                            "nombre": nombre_nuevo,
                            "tipo": tipo_nuevo,
                            "activo": True,
                        }).execute()

                        registrar_evento("CREAR_PLATO", nombre_nuevo)
                        refrescar()
                        st.success("Plato añadido y activado.")
                        st.rerun()

                    except Exception as e:
                        error_ui(e, "guardar el plato")

        catalogo = catalogo_cargar()

        if catalogo:
            activos = sum(1 for p in catalogo if esta_activo(p))
            inactivos = len(catalogo) - activos

            a, b, c = st.columns(3)
            a.metric("Total de platos", len(catalogo))
            b.metric("Platos activos", activos)
            c.metric("Platos desactivados", inactivos)

            st.write("")
            filtro_estado = st.selectbox(
                "Mostrar platos",
                [
                    "Todos los platos",
                    "Solo activos",
                    "Solo desactivados",
                ],
                key="filtro_catalogo",
            )

            if filtro_estado == "Solo activos":
                catalogo_vista = [
                    p for p in catalogo if esta_activo(p)
                ]
            elif filtro_estado == "Solo desactivados":
                catalogo_vista = [
                    p for p in catalogo if not esta_activo(p)
                ]
            else:
                catalogo_vista = catalogo

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo(
                "Administración rápida",
                "Usa los botones para activar o desactivar cada plato. "
                "No se borra ningún registro.",
            )

            buscar_plato = st.text_input(
                "🔎 Buscar plato por nombre o categoría",
                key="buscar_plato_catalogo",
            )

            for plato in catalogo_vista:
                nombre_plato = limpio(plato.get("nombre"))
                categoria_plato = limpio(plato.get("tipo"))

                texto_busqueda = (
                    nombre_plato + " " + categoria_plato
                ).casefold()

                if buscar_plato and buscar_plato.casefold() not in texto_busqueda:
                    continue

                col_info, col_estado, col_accion = st.columns([3, 1.2, 1.5])

                with col_info:
                    st.markdown(f"**{nombre_plato}**")
                    st.caption(
                        f"Categoría: {categoria_plato} · ID: {plato.get('id')}"
                    )

                with col_estado:
                    if esta_activo(plato):
                        st.success("● Activo")
                    else:
                        st.warning("● Desactivado")

                with col_accion:
                    if esta_activo(plato):
                        texto_boton = "Desactivar"
                    else:
                        texto_boton = "Activar"

                    if st.button(
                        texto_boton,
                        key=f"estado_plato_{plato.get('id')}",
                        use_container_width=True,
                    ):
                        try:
                            cambiar_estado_plato(plato)
                            st.success(
                                f"Se actualizó el estado de {nombre_plato}."
                            )
                            st.rerun()
                        except Exception as e:
                            error_ui(e, "cambiar el estado del plato")

                st.divider()

            st.markdown('</div>', unsafe_allow_html=True)

            # Tabla completa y exportación del catálogo.
            tabla = [{
                "ID": p.get("id"),
                "Categoría": p.get("tipo", ""),
                "Plato": p.get("nombre", ""),
                "Estado": "Activo" if esta_activo(p) else "Desactivado",
            } for p in catalogo]

            with st.expander("📋 Ver tabla completa y exportar"):
                st.dataframe(
                    pd.DataFrame(tabla),
                    use_container_width=True,
                    hide_index=True,
                )
                exportar(tabla, "catalogo_platos")

            # Se mantiene la edición existente de cada plato.
            ids = [
                p.get("id") for p in catalogo
                if p.get("id") is not None
            ]

            st.write("")
            st.markdown("### ✏️ Editar información de un plato")

            pid = st.selectbox(
                "Selecciona un plato para editar",
                ids,
                format_func=lambda x: f"#{x} — " + next(
                    (
                        str(p.get("nombre", ""))
                        for p in catalogo
                        if str(p.get("id")) == str(x)
                    ),
                    "",
                ),
                key="plato_editar_id",
            )

            plato_editar = next(
                p for p in catalogo
                if str(p.get("id")) == str(pid)
            )

            with st.form("editar_plato"):
                nombre_editar = st.text_input(
                    "Nombre",
                    value=str(plato_editar.get("nombre", "")),
                )

                tipos = ["Entrada", "Segundo", "Bebida", "Extra", "Otro"]
                tipo_actual = str(plato_editar.get("tipo", "Otro"))

                if tipo_actual not in tipos:
                    tipos.append(tipo_actual)

                tipo_editar = st.selectbox(
                    "Categoría",
                    tipos,
                    index=tipos.index(tipo_actual),
                )

                activo_editar = st.checkbox(
                    "Plato activo",
                    value=esta_activo(plato_editar),
                )

                guardar_edicion = st.form_submit_button(
                    "Guardar cambios",
                    type="primary",
                )

            if guardar_edicion:
                nombre_editar = limpio(nombre_editar)

                duplicado = any(
                    str(otro.get("id")) != str(pid)
                    and limpio(otro.get("nombre")).casefold()
                    == nombre_editar.casefold()
                    and str(otro.get("tipo", "")).casefold()
                    == tipo_editar.casefold()
                    for otro in catalogo
                )

                if not nombre_editar:
                    st.error("El nombre no puede estar vacío.")
                elif duplicado:
                    st.error("Ya existe otro plato con ese nombre y categoría.")
                else:
                    try:
                        db.table("catalogo_platos").update({
                            "nombre": nombre_editar,
                            "tipo": tipo_editar,
                            "activo": activo_editar,
                        }).eq("id", pid).execute()

                        registrar_evento(
                            "EDITAR_PLATO",
                            f"{nombre_editar} - activo: {activo_editar}",
                        )

                        refrescar()
                        st.success("Plato actualizado.")
                        st.rerun()

                    except Exception as e:
                        error_ui(e, "actualizar el plato")

        else:
            st.info("Tu catálogo está vacío. Agrega tu primer plato arriba.")

    except Exception as e:
        error_ui(e, "cargar el catálogo")


# =========================================================
# SISTEMA
# =========================================================

elif pagina == "Sistema":
    banner(
        "Sistema",
        "Estado de conexión y actividad de la aplicación.",
    )

    a, b = st.columns(2)

    with a:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_titulo("Información")
        st.write("**Aplicación:** Como en Casa Dely")
        st.write(f"**Versión:** {VERSION}")
        st.write("**Base de datos:** Supabase")
        st.markdown('</div>', unsafe_allow_html=True)

    with b:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_titulo("Conexión")

        if st.button("Comprobar conexión", type="primary"):
            try:
                db.table("pedidos").select("id").limit(1).execute()
                st.success("Conexión con Supabase correcta.")
            except Exception as e:
                error_ui(e, "comprobar la conexión")

        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### Registro de actividad")

    try:
        eventos = leer("registro_sistema")
        eventos.sort(
            key=lambda x: str(x.get("fecha") or ""),
            reverse=True,
        )

        if eventos:
            st.dataframe(
                pd.DataFrame(eventos[:200]),
                use_container_width=True,
                hide_index=True,
            )
            exportar(eventos[:200], "registro_sistema")
        else:
            st.info("Todavía no hay actividad registrada.")

    except Exception as e:
        error_ui(e, "leer el registro del sistema")


# =========================================================
# PIE
# =========================================================

st.markdown(
    "<div style='text-align:center;padding:24px 0 4px;color:#897C6E;"
    "font-size:.8rem'>🍗 Como en Casa Dely · Hecho para gestionar mejor tu negocio</div>",
    unsafe_allow_html=True,
)
