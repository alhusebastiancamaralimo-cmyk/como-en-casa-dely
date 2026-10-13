
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Como en Casa Dely",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales
st.markdown("""
<style>
.stApp {
    background-color: #FFF9F0;
}
h1, h2, h3 {
    color: #8B2F23;
}
div.stButton > button {
    background-color: #8B2F23;
    color: white;
    border-radius: 10px;
    border: none;
    min-height: 42px;
}
div.stButton > button:hover {
    background-color: #B94A36;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Encabezado
st.title("🍗 Como en Casa Dely")
st.caption("Sistema de gestión de pedidos y ventas")

st.divider()

# Navegación
pagina = st.sidebar.radio(
    "📌 MENÚ PRINCIPAL",
    [
        "Registrar pedido",
        "Pedidos",
        "Estadísticas",
        "Configuración"
    ]
)

if pagina == "Registrar pedido":
    st.header("📝 Registrar nuevo pedido")
    st.info("Completa los datos del pedido. Los cambios todavía no se guardan permanentemente.")

    with st.form("formulario_pedido"):
        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("👤 Nombre del cliente")
            empresa = st.text_input("🏢 Empresa (opcional)")
            fecha_pedido = st.date_input(
                "📅 Fecha del pedido",
                value=date.today()
            )

        with col2:
            precio_menu = st.number_input(
                "💰 Precio por menú (S/)",
                min_value=10.0,
                max_value=20.0,
                value=15.0,
                step=0.5
            )
            cantidad_menus = st.number_input(
                "🍱 Cantidad de menús vendidos",
                min_value=0,
                value=1,
                step=1
            )

        st.subheader("🍲 Detalles del menú")

        entradas = st.text_input(
            "🥣 Entradas",
            placeholder="Ej.: sopa, papa a la huancaína"
        )

        segundos = st.text_input(
            "🍛 Segundos",
            placeholder="Ej.: arroz con pollo, lomo saltado"
        )

        observaciones = st.text_area(
            "📌 Observaciones",
            placeholder="Indicaciones especiales del pedido..."
        )

        total = precio_menu * cantidad_menus

        st.markdown(
            f"### Total del pedido: S/ {total:.2f}"
        )

        enviado = st.form_submit_button(
            "✅ Registrar pedido",
            use_container_width=True
        )

    if enviado:
        if not cliente.strip():
            st.error("Escribe el nombre del cliente.")
        elif cantidad_menus < 1:
            st.error("La cantidad de menús debe ser al menos 1.")
        else:
            st.success(
                "Formulario validado. La conexión para guardar "
                "el pedido se implementará en el siguiente paso."
            )
            st.write("**Cliente:**", cliente)
            st.write("**Fecha:**", fecha_pedido.strftime("%d/%m/%Y"))
            st.write("**Empresa:**", empresa or "No indicada")
            st.write("**Entradas:**", entradas or "No indicadas")
            st.write("**Segundos:**", segundos or "No indicados")
            st.write("**Cantidad de menús:**", cantidad_menus)
            st.write("**Total:**", f"S/ {total:.2f}")
            if observaciones:
                st.write("**Observaciones:**", observaciones)

elif pagina == "Pedidos":
    st.header("📋 Pedidos")
    st.info("Aquí aparecerán los pedidos guardados cuando conectemos la base de datos.")

elif pagina == "Estadísticas":
    st.header("📊 Estadísticas")
    st.info("Aquí mostraremos las ventas diarias, mensuales y por cliente.")

elif pagina == "Configuración":
    st.header("⚙️ Configuración")
    st.write("**Negocio:** Como en Casa Dely")
    st.write("**Moneda:** Soles peruanos (S/)")
    st.write("**Historial antiguo:** Archivado y separado del sistema nuevo.")
    st.info("Más adelante configuraremos usuarios, permisos y conexión a la base de datos.")
