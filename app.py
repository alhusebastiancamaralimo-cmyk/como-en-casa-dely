
import streamlit as st
from datetime import date
from supabase import create_client

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍗",
    layout="wide"
)

# ---------- ESTILO ----------
st.markdown("""
<style>
.stApp { background-color: #FFF9F0; }
h1, h2, h3 { color: #8B2F23; }
div.stButton > button {
    background-color: #8B2F23;
    color: white;
    border-radius: 10px;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)


# ---------- ACCESO ----------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🍗 Como en Casa Dely")
    st.subheader("Acceso al sistema")

    with st.form("inicio_sesion"):
        password = st.text_input(
            "Contraseña de acceso",
            type="password"
        )
        entrar = st.form_submit_button("Ingresar")

    if entrar:
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")

    st.stop()


# ---------- CONEXIÓN ----------
@st.cache_resource
def conectar_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    db = conectar_supabase()
except Exception:
    st.error(
        "No se pudo conectar a la base de datos. "
        "Revisa la configuración de Secrets."
    )
    st.stop()


# ---------- FUNCIONES ----------
def guardar_pedido(
    fecha, cliente, empresa, precio,
    cantidad, observaciones, entradas, segundos
):
    total = round(precio * cantidad, 2)

    respuesta = db.table("pedidos").insert({
        "fecha": fecha.isoformat(),
        "cliente": cliente.strip(),
        "empresa": empresa.strip() or None,
        "precio_menu": precio,
        "cantidad_menus": cantidad,
        "total": total,
        "observaciones": observaciones.strip() or None
    }).execute()

    pedido = respuesta.data[0]
    pedido_id = pedido["id"]

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


# ---------- INTERFAZ ----------
st.title("🍗 Como en Casa Dely")
st.caption("Gestión de pedidos y ventas")
st.sidebar.title("📌 Menú principal")

pagina = st.sidebar.radio(
    "Selecciona una sección",
    ["Registrar pedido", "Pedidos", "Estadísticas"]
)

if st.sidebar.button("Cerrar sesión"):
    st.session_state.autenticado = False
    st.rerun()


# ---------- REGISTRAR ----------
if pagina == "Registrar pedido":
    st.header("📝 Registrar pedido")

    with st.form("formulario_pedido"):
        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("Nombre del cliente")
            empresa = st.text_input("Empresa (opcional)")
            fecha_pedido = st.date_input(
                "Fecha del pedido",
                value=date.today()
            )

        with col2:
            precio = st.number_input(
                "Precio por menú (S/)",
                min_value=10.0,
                max_value=20.0,
                value=15.0,
                step=0.5
            )
            cantidad = st.number_input(
                "Cantidad de menús vendidos",
                min_value=1,
                value=1,
                step=1
            )

        st.subheader("🍲 Detalles del menú")
        entradas = st.text_input(
            "Entradas",
            placeholder="Sopa, papa a la huancaína"
        )
        segundos = st.text_input(
            "Segundos",
            placeholder="Arroz con pollo, lomo saltado"
        )
        observaciones = st.text_area("Observaciones")

        total = precio * cantidad
        st.markdown(f"### Total: S/ {total:.2f}")

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
                    int(cantidad),
                    observaciones,
                    entradas,
                    segundos
                )
                st.success(
                    f"Pedido #{pedido_id} guardado. "
                    f"Total: S/ {total_guardado:.2f}"
                )
            except Exception:
                st.error(
                    "No se pudo guardar el pedido. "
                    "Revisa la conexión y los permisos de la base de datos."
                )


# ---------- LISTA DE PEDIDOS ----------
elif pagina == "Pedidos":
    st.header("📋 Pedidos guardados")

    try:
        respuesta = (
            db.table("pedidos")
            .select("*")
            .order("fecha", desc=True)
            .order("id", desc=True)
            .limit(200)
            .execute()
        )

        pedidos = respuesta.data

        if pedidos:
            st.dataframe(
                pedidos,
                use_container_width=True,
                hide_index=True
            )
            st.caption(
                "Se muestran hasta 200 pedidos recientes."
            )
        else:
            st.info("Todavía no hay pedidos guardados.")
    except Exception:
        st.error("No se pudieron consultar los pedidos.")


# ---------- ESTADÍSTICAS ----------
elif pagina == "Estadísticas":
    st.header("📊 Estadísticas")

    try:
        respuesta = (
            db.table("pedidos")
            .select("fecha,cantidad_menus,total")
            .execute()
        )

        pedidos = respuesta.data
        hoy = date.today().isoformat()

        pedidos_hoy = [
            p for p in pedidos if p["fecha"] == hoy
        ]

        menus_hoy = sum(
            int(p["cantidad_menus"]) for p in pedidos_hoy
        )
        ventas_hoy = sum(
            float(p["total"]) for p in pedidos_hoy
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Pedidos de hoy", len(pedidos_hoy))
        c2.metric("Menús vendidos", menus_hoy)
        c3.metric("Ventas de hoy", f"S/ {ventas_hoy:.2f}")

    except Exception:
        st.error("No se pudieron calcular las estadísticas.")
