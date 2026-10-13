
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

VERSION = "5.0.0"

# =========================================================
# DISEÑO VISUAL
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --fondo: #F7F4EF;
    --blanco: #FFFFFF;
    --cafe: #5A3928;
    --cafe-oscuro: #38251C;
    --terracota: #B87552;
    --arena: #E9D9C6;
    --texto: #382D26;
    --suave: #8C8178;
    --verde: #547A61;
    --borde: #EAE3DA;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--fondo);
    color: var(--texto);
}

[data-testid="stHeader"] {
    background: rgba(247,244,239,0.95);
}

[data-testid="stSidebar"] {
    background: var(--cafe-oscuro);
    border-right: none;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.4rem;
}

[data-testid="stSidebar"] * {
    color: #F8F0E7;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #D9C7B7;
}

[data-testid="stSidebar"] hr {
    border-color: #665044;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 7px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 9px 11px;
    transition: background .2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #674735;
}

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

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.marca {
    background: linear-gradient(115deg, #38251C 0%, #684832 60%, #9D6D4B 100%);
    border-radius: 20px;
    padding: 25px 30px;
    margin-bottom: 25px;
    color: #FFF8F0;
    box-shadow: 0 8px 24px rgba(56,37,28,.12);
    position: relative;
    overflow: hidden;
}

.marca:after {
    content: "✦";
    position: absolute;
    right: 34px;
    top: -28px;
    font-size: 130px;
    color: rgba(255,255,255,.07);
}

.marca h1 {
    color: #FFF8F0 !important;
    font-size: 2rem !important;
    margin: 0 0 5px 0;
}

.marca p {
    color: #E8D7C7 !important;
    margin: 0;
    font-size: .95rem;
}

.etiqueta {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 30px;
    background: rgba(255,255,255,.13);
    color: #FFF8F0;
    font-size: .75rem;
    margin-bottom: 12px;
    letter-spacing: .5px;
}

.tarjeta {
    background: #FFFFFF;
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
    background: #FFFFFF;
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
    background: white;
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

[data-testid="stMetricDelta"] {
    font-size: .8rem;
}

div.stButton > button,
div.stDownloadButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    border-color: var(--borde);
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
    border-color: var(--terracota);
    color: var(--terracota);
}

div.stButton > button[kind="primary"]:hover {
    background: var(--cafe-oscuro);
    color: white;
}

div[data-testid="stForm"] {
    background: white;
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
    color: var(--terracota);
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
# FUNCIONES
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
        return pd.to_datetime(valor, errors="coerce").date()
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

    return (f"Dirección: {direccion}\n{notas}".strip()
            if direccion else notas)


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
        f'<div class="marca"><div class="etiqueta">COMO EN CASA DELY · ADMINISTRACIÓN</div>'
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
# NAVEGACIÓN
# =========================================================

with st.sidebar:
    st.markdown(
        "<div style='font-size:2rem'>🍗</div>"
        "<div style='font-family:Playfair Display,serif;font-size:1.3rem;"
        "font-weight:700;color:#FFF8F0'>Como en Casa Dely</div>"
        "<div style='font-size:.78rem;color:#D9C7B7'>Panel de administración</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    paginas = [
        "Inicio",
        "Registrar pedido",
        "Pedidos",
        "Estadísticas",
        "Empresas",
        "Catálogo",
        "Sistema",
    ]

    pagina = st.radio(
        "NAVEGACIÓN",
        paginas,
        index=paginas.index(st.session_state.get("pagina", "Inicio")),
        label_visibility="collapsed",
    )
    st.session_state.pagina = pagina

    st.divider()
    st.caption("GESTIÓN DEL NEGOCIO")
    st.caption(f"Versión {VERSION}")

    if st.button("↻ Actualizar datos", use_container_width=True):
        refrescar()
        st.rerun()

    if PASSWORD and st.button("Cerrar sesión", use_container_width=True):
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
        activas = sum(1 for e in empresas if e.get("activo", True))

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
            panel_titulo("📊 Evolución de ventas", "Ingresos diarios de los últimos 14 días")

            desde = hoy - timedelta(days=13)
            por_dia = {}

            for p in pedidos:
                f = fecha_segura(p.get("fecha"))
                if f and desde <= f <= hoy:
                    clave = f.strftime("%d %b")
                    por_dia[clave] = por_dia.get(clave, 0) + float(p.get("total") or 0)

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
            panel_titulo("🏆 Empresas principales", "Según las ventas de este mes")

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
                        f"<span style='color:#B87552;font-size:1.1rem;font-weight:700'>"
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
# =========================================================

elif pagina == "Registrar pedido":
    banner("Nuevo pedido", "Registra los detalles y calcula el total automáticamente.")

    if st.session_state.pop("limpiar_pedido", False):
        for k in [
            "cliente", "empresa_pedido", "direccion_pedido", "precio",
            "cantidad", "entrada", "segundo", "bebida", "notas",
            "fecha_pedido",
        ]:
            st.session_state.pop(k, None)

    try:
        empresas = [
            e for e in empresas_cargar()
            if e.get("activo", True)
        ]
        opciones = ["Sin empresa"] + sorted(
            {limpio(e.get("nombre")) for e in empresas if limpio(e.get("nombre"))}
        )

        with st.form("form_pedido"):
            st.markdown("#### 👤 Datos del cliente")
            c1, c2 = st.columns(2)

            with c1:
                cliente = st.text_input("Nombre del cliente *", key="cliente")
                empresa = st.selectbox("Empresa", opciones, key="empresa_pedido")
                direccion = st.text_input("Dirección de entrega", key="direccion_pedido")

            with c2:
                fecha_pedido = st.date_input("Fecha del pedido", value=date.today(), key="fecha_pedido")
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

            st.divider()
            st.markdown("#### 🍽️ Detalles de la comida")
            c1, c2, c3 = st.columns(3)

            with c1:
                entrada = st.text_input("Entrada", key="entrada")
            with c2:
                segundo = st.text_input("Segundo", key="segundo")
            with c3:
                bebida = st.text_input("Bebida o adicional", key="bebida")

            notas = st.text_area("Observaciones", key="notas")
            total = float(precio) * int(cantidad)

            st.info(f"**Total del pedido: {dinero(total)}**")

            guardar = st.form_submit_button(
                "💾 Guardar pedido",
                type="primary",
                use_container_width=True,
            )

        if guardar:
            if not limpio(cliente):
                st.error("Escribe el nombre del cliente.")
            elif precio <= 0:
                st.error("El precio debe ser mayor que cero.")
            else:
                registro = {
                    "fecha": fecha_pedido.isoformat(),
                    "cliente": limpio(cliente),
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
                        except Exception:
                            try:
                                db.table("pedidos").delete().eq("id", pedido_id).execute()
                            except Exception:
                                pass
                            raise RuntimeError(
                                "Falló el guardado de los detalles. "
                                "Se intentó cancelar el pedido."
                            )

                    registrar_evento("CREAR_PEDIDO", f"Pedido {pedido_id}")
                    refrescar()
                    st.session_state.limpiar_pedido = True
                    st.success(f"Pedido #{pedido_id} registrado por {dinero(total)}.")
                    st.rerun()

                except Exception as e:
                    error_ui(e, "guardar el pedido")

    except Exception as e:
        error_ui(e, "cargar las empresas")


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
                desde = st.date_input("Desde", date.today() - timedelta(days=30))
            with b:
                hasta = st.date_input("Hasta", date.today())

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
                direccion, notas = direccion_y_notas(p.get("observaciones", ""))
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
            st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
            exportar(filas, "pedidos")
            st.markdown('</div>', unsafe_allow_html=True)

            ids = [p.get("id") for p in filtrados if p.get("id") is not None]

            if ids:
                st.write("")
                st.markdown("### Administrar pedido")
                pid = st.selectbox(
                    "Selecciona un pedido",
                    ids,
                    format_func=lambda x: f"Pedido #{x} — " + next(
                        (str(p.get("cliente", "")) for p in filtrados if str(p.get("id")) == str(x)),
                        "",
                    ),
                )
                p = next(p for p in filtrados if str(p.get("id")) == str(pid))
                direccion_actual, notas_actuales = direccion_y_notas(p.get("observaciones", ""))

                with st.expander("✏️ Editar datos"):
                    with st.form("editar_pedido"):
                        cliente = st.text_input("Cliente", value=str(p.get("cliente", "")))
                        empresa = st.text_input("Empresa", value=str(p.get("empresa", "")))
                        direccion = st.text_input("Dirección", value=direccion_actual)
                        fecha_actual = fecha_segura(p.get("fecha")) or date.today()
                        fecha_pedido = st.date_input("Fecha", value=fecha_actual)
                        precio = st.number_input(
                            "Precio por menú",
                            min_value=0.0,
                            value=float(p.get("precio_menu") or 0),
                            step=0.5,
                        )
                        cantidad = st.number_input(
                            "Cantidad de menús",
                            min_value=1,
                            max_value=10000,
                            value=max(1, int(p.get("cantidad_menus") or 1)),
                        )
                        notas = st.text_area("Observaciones", value=notas_actuales)
                        actualizar = st.form_submit_button("Guardar cambios", type="primary")

                    if actualizar:
                        if not limpio(cliente):
                            st.error("El cliente no puede quedar vacío.")
                        elif precio <= 0:
                            st.error("El precio debe ser mayor que cero.")
                        else:
                            try:
                                db.table("pedidos").update({
                                    "fecha": fecha_pedido.isoformat(),
                                    "cliente": limpio(cliente),
                                    "empresa": limpio(empresa),
                                    "precio_menu": float(precio),
                                    "cantidad_menus": int(cantidad),
                                    "total": round(float(precio) * int(cantidad), 2),
                                    "observaciones": observaciones_finales(direccion, notas),
                                }).eq("id", pid).execute()

                                registrar_evento("EDITAR_PEDIDO", f"Pedido {pid}")
                                refrescar()
                                st.success("Pedido actualizado.")
                                st.rerun()
                            except Exception as e:
                                error_ui(e, "actualizar el pedido")

                with st.expander("🗑️ Eliminar pedido"):
                    st.warning("Se eliminará el pedido y sus detalles. Esta acción no se puede deshacer.")
                    confirmar = st.checkbox("Confirmo que quiero eliminarlo", key=f"confirmar_{pid}")

                    if st.button("Eliminar pedido", disabled=not confirmar, type="primary"):
                        try:
                            db.table("detalle_pedido").delete().eq("pedido_id", pid).execute()
                            db.table("pedidos").delete().eq("id", pid).execute()
                            registrar_evento("ELIMINAR_PEDIDO", f"Pedido {pid}", "AVISO")
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
    banner("Estadísticas", "Entiende tus ventas y toma mejores decisiones.")

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
                    value=max(min(fechas), date.today() - timedelta(days=30)),
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
                    por_empresa[nombre] = por_empresa.get(nombre, 0) + float(p.get("total") or 0)

                if por_empresa:
                    df = pd.DataFrame([
                        {"Empresa": k, "Ventas": v}
                        for k, v in sorted(por_empresa.items(), key=lambda x: x[1], reverse=True)
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
                        por_dia[f.isoformat()] = por_dia.get(f.isoformat(), 0) + float(p.get("total") or 0)

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
    banner("Empresas", "Administra tus clientes empresariales de forma independiente.")

    try:
        empresas = empresas_cargar()

        with st.expander("＋ Registrar empresa", expanded=not bool(empresas)):
            with st.form("crear_empresa"):
                nombre = st.text_input("Nombre de empresa *")
                contacto = st.text_input("Persona de contacto")
                telefono = st.text_input("Teléfono")
                direccion = st.text_input("Dirección")
                notas = st.text_area("Observaciones")
                guardar = st.form_submit_button("Guardar empresa", type="primary")

            if guardar:
                nombre = limpio(nombre)

                if not nombre:
                    st.error("Escribe el nombre de la empresa.")
                elif any(limpio(e.get("nombre")).casefold() == nombre.casefold() for e in empresas):
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
                "Estado": "Activa" if e.get("activo", True) else "Inactiva",
            } for e in empresas]

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo("Directorio de empresas", f"{len(empresas)} empresas registradas")
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, hide_index=True)
            exportar(tabla, "empresas")
            st.markdown('</div>', unsafe_allow_html=True)

            ids = [e.get("id") for e in empresas if e.get("id") is not None]

            st.write("")
            st.markdown("### Editar empresa")
            eid = st.selectbox(
                "Selecciona una empresa",
                ids,
                format_func=lambda x: f"#{x} — " + next(
                    (str(e.get("nombre", "")) for e in empresas if str(e.get("id")) == str(x)),
                    "",
                ),
            )
            e = next(e for e in empresas if str(e.get("id")) == str(eid))

            with st.form("editar_empresa"):
                nombre = st.text_input("Nombre", value=str(e.get("nombre", "")))
                contacto = st.text_input("Contacto", value=str(e.get("contacto", "")))
                telefono = st.text_input("Teléfono", value=str(e.get("telefono", "")))
                direccion = st.text_input("Dirección", value=str(e.get("direccion", "")))
                notas = st.text_area("Observaciones", value=str(e.get("observaciones", "")))
                activo = st.checkbox("Empresa activa", value=bool(e.get("activo", True)))
                actualizar = st.form_submit_button("Guardar cambios", type="primary")

            if actualizar:
                nombre_nuevo = limpio(nombre)
                duplicada = any(
                    str(otra.get("id")) != str(eid)
                    and limpio(otra.get("nombre")).casefold() == nombre_nuevo.casefold()
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
                            "contacto": limpio(contacto),
                            "telefono": limpio(telefono),
                            "direccion": limpio(direccion),
                            "observaciones": notas,
                            "activo": activo,
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
# =========================================================

elif pagina == "Catálogo":
    banner("Catálogo de platos", "Organiza tus entradas, segundos, bebidas y adicionales.")

    try:
        catalogo = catalogo_cargar()

        with st.expander("＋ Agregar plato", expanded=not bool(catalogo)):
            with st.form("crear_plato"):
                nombre = st.text_input("Nombre del plato *")
                tipo = st.selectbox("Categoría", ["Entrada", "Segundo", "Bebida", "Extra", "Otro"])
                guardar = st.form_submit_button("Guardar plato", type="primary")

            if guardar:
                nombre = limpio(nombre)

                if not nombre:
                    st.error("Escribe el nombre del plato.")
                elif any(
                    limpio(p.get("nombre")).casefold() == nombre.casefold()
                    and str(p.get("tipo", "")).casefold() == tipo.casefold()
                    for p in catalogo
                ):
                    st.error("Ese plato ya existe en esa categoría.")
                else:
                    try:
                        db.table("catalogo_platos").insert({
                            "nombre": nombre,
                            "tipo": tipo,
                            "activo": True,
                        }).execute()
                        registrar_evento("CREAR_PLATO", nombre)
                        refrescar()
                        st.success("Plato añadido.")
                        st.rerun()
                    except Exception as e:
                        error_ui(e, "guardar el plato")

        catalogo = catalogo_cargar()

        if catalogo:
            tabla = [{
                "ID": p.get("id"),
                "Categoría": p.get("tipo", ""),
                "Plato": p.get("nombre", ""),
                "Estado": "Activo" if p.get("activo", True) else "Inactivo",
            } for p in catalogo]

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_titulo("Platos registrados", f"{len(catalogo)} productos en el catálogo")
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            ids = [p.get("id") for p in catalogo if p.get("id") is not None]
            st.write("")
            st.markdown("### Editar plato")
            pid = st.selectbox(
                "Selecciona un plato",
                ids,
                format_func=lambda x: f"#{x} — " + next(
                    (str(p.get("nombre", "")) for p in catalogo if str(p.get("id")) == str(x)),
                    "",
                ),
            )
            p = next(p for p in catalogo if str(p.get("id")) == str(pid))

            with st.form("editar_plato"):
                nombre = st.text_input("Nombre", value=str(p.get("nombre", "")))
                tipos = ["Entrada", "Segundo", "Bebida", "Extra", "Otro"]
                tipo_actual = str(p.get("tipo", "Otro"))
                if tipo_actual not in tipos:
                    tipos.append(tipo_actual)
                tipo = st.selectbox("Categoría", tipos, index=tipos.index(tipo_actual))
                activo = st.checkbox("Plato activo", value=bool(p.get("activo", True)))
                actualizar = st.form_submit_button("Guardar cambios", type="primary")

            if actualizar:
                if not limpio(nombre):
                    st.error("El nombre no puede estar vacío.")
                else:
                    try:
                        db.table("catalogo_platos").update({
                            "nombre": limpio(nombre),
                            "tipo": tipo,
                            "activo": activo,
                        }).eq("id", pid).execute()
                        registrar_evento("EDITAR_PLATO", limpio(nombre))
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
    banner("Sistema", "Estado de conexión y actividad de la aplicación.")

    a, b = st.columns(2)
    with a:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_titulo("Información")
        st.write(f"**Aplicación:** Como en Casa Dely")
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
        eventos.sort(key=lambda x: str(x.get("fecha") or ""), reverse=True)

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
    "<div style='text-align:center;padding:24px 0 4px;color:#97897D;"
    "font-size:.8rem'>🍗 Como en Casa Dely · Hecho para gestionar mejor tu negocio</div>",
    unsafe_allow_html=True,
)
