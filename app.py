import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SurveyPilot - Radar de Encuestas en Tiempo Real",
    page_icon="gemini-svg.svg",
    layout="wide"
)

# --- BASE DE DATOS LOCAL (sqlite) ---
def init_db():
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    # Historial de ganancias del usuario
    c.execute('''
        CREATE TABLE IF NOT EXISTS mis_ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            plataforma TEXT,
            titulo_encuesta TEXT,
            duracion_min INTEGER,
            ganancia_eur REAL,
            ratio_eur_hora REAL
        )
    ''')
    # Encuestas publicadas en el radar
    c.execute('''
        CREATE TABLE IF NOT EXISTS encuestas_publicadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            plataforma TEXT,
            pago_eur REAL,
            duracion_min INTEGER,
            categoria TEXT,
            paises TEXT,
            metodo_pago TEXT,
            enlace TEXT,
            nivel_confianza TEXT
        )
    ''')
    # Memoria de enlaces de afiliados por plataforma
    c.execute('''
        CREATE TABLE IF NOT EXISTS enlaces_afiliados (
            plataforma TEXT PRIMARY KEY,
            enlace TEXT
        )
    ''')
    
    # Pre-cargar tus enlaces de afiliado reales por defecto
    enlaces_iniciales = [
        ("AttaPoll", "https://attapoll.app/join/pympx"),
        ("Freecash", "https://freecash.com/r/39ZATU"),
        ("Heycash", "https://heycash.com/register?ref=a2bcf3b1-b674-4bba-af6e-d92b5e16a7d7")
    ]
    for plat, link in enlaces_iniciales:
        c.execute('''
            INSERT OR IGNORE INTO enlaces_afiliados (plataforma, enlace)
            VALUES (?, ?)
        ''', (plat, link))

    conn.commit()
    conn.close()

def registrar_ingreso(plataforma, titulo, duracion_min, ganancia_eur):
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    ratio = (ganancia_eur / (duracion_min / 60)) if duracion_min > 0 else 0.0
    c.execute('''
        INSERT INTO mis_ingresos (fecha, plataforma, titulo_encuesta, duracion_min, ganancia_eur, ratio_eur_hora)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (fecha_actual, plataforma, titulo, duracion_min, ganancia_eur, ratio))
    conn.commit()
    conn.close()

def obtener_ingresos():
    conn = sqlite3.connect("surveypilot.db")
    df = pd.read_sql_query("SELECT * FROM mis_ingresos ORDER BY id DESC", conn)
    conn.close()
    return df

def guardar_enlace_afiliado(plataforma, enlace):
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO enlaces_afiliados (plataforma, enlace)
        VALUES (?, ?)
    ''', (plataforma.strip(), enlace.strip()))
    conn.commit()
    conn.close()

def obtener_enlace_afiliado(plataforma):
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    c.execute("SELECT enlace FROM enlaces_afiliados WHERE LOWER(plataforma) = LOWER(?)", (plataforma.strip(),))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def publicar_encuesta_db(titulo, plataforma, pago_eur, duracion_min, categoria, paises, metodo_pago, enlace, nivel_confianza):
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO encuestas_publicadas (titulo, plataforma, pago_eur, duracion_min, categoria, paises, metodo_pago, enlace, nivel_confianza)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, plataforma, pago_eur, duracion_min, categoria, paises, metodo_pago, enlace, nivel_confianza))
    conn.commit()
    conn.close()

def obtener_encuestas_publicadas():
    conn = sqlite3.connect("surveypilot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM encuestas_publicadas ORDER BY id DESC")
    filas = c.fetchall()
    conn.close()
    
    encuestas = []
    for f in filas:
        pago = f[3]
        duracion = f[4]
        ratio = round(pago / (duracion / 60), 2) if duracion > 0 else 0.0
        encuestas.append({
            "id": f[0],
            "titulo": f[1],
            "plataforma": f[2],
            "pago_eur": pago,
            "duracion_min": duracion,
            "categoria": f[5],
            "paises": f[6].split(", "),
            "metodo_pago": f[7],
            "enlace": f[8],
            "nivel_confianza": f[9],
            "ratio_eur_hora": ratio
        })
    return encuestas

init_db()

# --- DATOS BASE CON TUS ENLACES DE AFILIADO REALES ---
ENCUESTAS_BASE_DEFAULT = [
    {
        "id": 1,
        "titulo": "Opinión sobre Marcas de Automóviles Eléctricos y Movilidad",
        "plataforma": "AttaPoll",
        "pago_eur": 1.80,
        "duracion_min": 8,
        "categoria": "Estudio de Mercado",
        "paises": ["España", "México", "Argentina", "Internacional"],
        "metodo_pago": "PayPal / Gift Cards / Revolut",
        "enlace": "https://attapoll.app/join/pympx",
        "nivel_confianza": "Medio-Alto",
        "ratio_eur_hora": 13.50
    },
    {
        "id": 2,
        "titulo": "Encuesta sobre Servicios de Streaming, Música y Juegos",
        "plataforma": "Freecash",
        "pago_eur": 2.50,
        "duracion_min": 12,
        "categoria": "Consumo y Entretenimiento",
        "paises": ["España", "México", "Argentina", "Internacional"],
        "metodo_pago": "Crypto / PayPal / Amazon",
        "enlace": "https://freecash.com/r/39ZATU",
        "nivel_confianza": "Alto",
        "ratio_eur_hora": 12.50
    },
    {
        "id": 3,
        "titulo": "Cuestionario de Hábitos de Compra y Estilo de Vida",
        "plataforma": "Heycash",
        "pago_eur": 2.00,
        "duracion_min": 10,
        "categoria": "Estudio de Mercado",
        "paises": ["España", "Internacional"],
        "metodo_pago": "PayPal / Tarjetas Regalo",
        "enlace": "https://heycash.com/register?ref=a2bcf3b1-b674-4bba-af6e-d92b5e16a7d7",
        "nivel_confianza": "Alto",
        "ratio_eur_hora": 12.00
    },
    {
        "id": 4,
        "titulo": "Estudio de Consumo Digital y Redes Sociales",
        "plataforma": "Prolific",
        "pago_eur": 3.50,
        "duracion_min": 15,
        "categoria": "Investigación Académica",
        "paises": ["España", "Internacional"],
        "metodo_pago": "PayPal",
        "enlace": "https://www.prolific.com/",
        "nivel_confianza": "Altísimo (Sin descalificación)",
        "ratio_eur_hora": 14.00
    }
]

encuestas_dinamicas = obtener_encuestas_publicadas()
ENCUESTAS_TOTALES = encuestas_dinamicas + ENCUESTAS_BASE_DEFAULT

# --- CABECERA PRINCIPAL ---
st.title("✈️ SurveyPilot")
st.caption("Radar Inteligente & Agregador de Encuestas en Tiempo Real")

# --- BARRA LATERAL (Filtros de usuario) ---
with st.sidebar:
    st.header("🎯 Filtros Rápidos")
    
    filtro_pais = st.selectbox(
        "Tu País:", 
        ["Todos", "España", "México", "Argentina", "Internacional"]
    )
    
    filtro_tiempo_max = st.slider("Tiempo máximo (min):", min_value=5, max_value=60, value=30, step=5)
    filtro_pago_min = st.slider("Pago mínimo (€):", min_value=0, max_value=10, value=1, step=1)
    
    filtro_categoria = st.multiselect(
        "Categorías:", 
        ["Investigación Académica", "Prueba de Software / UX", "Estudio de Mercado", "Entretenimiento", "Consumo", "Consumo y Entretenimiento", "Política y Sociedad"]
    )

# --- FILTRADO DE DATOS ---
encuestas_filtradas = ENCUESTAS_TOTALES.copy()

if filtro_pais != "Todos":
    encuestas_filtradas = [e for e in encuestas_filtradas if filtro_pais in e["paises"] or "Internacional" in e["paises"]]

encuestas_filtradas = [e for e in encuestas_filtradas if e["duracion_min"] <= filtro_tiempo_max and e["pago_eur"] >= filtro_pago_min]

if filtro_categoria:
    encuestas_filtradas = [e for e in encuestas_filtradas if e["categoria"] in filtro_categoria]

encuestas_filtradas = sorted(encuestas_filtradas, key=lambda x: x["ratio_eur_hora"], reverse=True)

# --- PESTAÑAS NAVEGACIÓN ---
tabs = st.tabs(["⚡ Radar en Vivo", "➕ Registrar Encuesta", "📊 Historial & Balance", "🔒 Panel Admin"])

# === PESTAÑA 1: RADAR DE ENCUESTAS ===
with tabs[0]:
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader(f"🔥 Encuestas Disponibles ({len(encuestas_filtradas)})")
    with col_t2:
        st.caption("🟢 Conexión API: **Sincronizada**")

    st.divider()

    if not encuestas_filtradas:
        st.warning("No hay encuestas con los filtros actuales. Ajusta los filtros de la barra lateral.")
    else:
        for e in encuestas_filtradas:
            if e["ratio_eur_hora"] >= 10.0:
                badge = f"🔥 RENTABILIDAD ALTA ({e['ratio_eur_hora']:.2f} €/h)"
            elif e["ratio_eur_hora"] >= 6.0:
                badge = f"✅ RENTABILIDAD BUENA ({e['ratio_eur_hora']:.2f} €/h)"
            else:
                badge = f"🟡 RENTABILIDAD NORMAL ({e['ratio_eur_hora']:.2f} €/h)"

            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1.5])
                
                with c1:
                    st.markdown(f"#### {e['titulo']}")
                    st.caption(f"🏛️ **Plataforma:** {e['plataforma']}  |  🏷️ {e['categoria']}")
                    st.write(f"🔒 {e['nivel_confianza']} | 💳 {e['metodo_pago']}")

                with c2:
                    st.markdown(f"### 💶 {e['pago_eur']:.2f} €")
                    st.write(f"⏱️ **Duración:** {e['duracion_min']} min")
                    st.markdown(f"`{badge}`")

                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.link_button("Ir a la Encuesta ↗", e['enlace'], type="primary", use_container_width=True)

                st.divider()

# === PESTAÑA 2: REGISTRAR ENCUESTA ===
with tabs[1]:
    st.subheader("➕ Registrar Encuesta Completada")
    with st.form("form_registro"):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            plat_input = st.text_input("Plataforma:", placeholder="Ej. AttaPoll")
            titulo_input = st.text_input("Título de la encuesta:")
        with col_r2:
            duracion_input = st.number_input("Tiempo (minutos):", min_value=1, value=15)
            ganancia_input = st.number_input("Ganancia (€):", min_value=0.01, value=2.00, step=0.10)

        btn_guardar = st.form_submit_button("Guardar en Historial", use_container_width=True)
        if btn_guardar:
            if plat_input.strip() != "":
                registrar_ingreso(plat_input, titulo_input, duracion_input, ganancia_input)
                st.success("🎉 ¡Guardado en tu historial!")
            else:
                st.warning("Introduce el nombre de la plataforma.")

# === PESTAÑA 3: HISTORIAL ===
with tabs[2]:
    st.subheader("📊 Historial Personal")
    df_ingresos = obtener_ingresos()

    if not df_ingresos.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        total_ganado = df_ingresos["ganancia_eur"].sum()
        total_min = df_ingresos["duracion_min"].sum()
        ratio_promedio = (total_ganado / (total_min / 60)) if total_min > 0 else 0.0

        col_m1.metric("Total Ganado", f"{total_ganado:.2f} €")
        col_m2.metric("Tiempo Total", f"{total_min} min")
        col_m3.metric("Ratio Promedio", f"{ratio_promedio:.2f} €/h")

        st.divider()
        st.dataframe(df_ingresos, use_container_width=True)
    else:
        st.info("Sin registros acumulados aún.")

# === PESTAÑA 4: PANEL DE ADMINISTRACIÓN INTELIGENTE ===
with tabs[3]:
    st.subheader("🔒 Panel de Control del Creador")
    clave_admin = st.text_input("Introduce la clave de Administrador:", type="password")
    
    if clave_admin == "admin123":
        st.success("Acceso concedido como Administrador de SurveyPilot")
        
        st.markdown("### 📢 Publicar Nueva Oferta / Encuesta")
        
        with st.form("form_publicar_oferta"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pub_titulo = st.text_input("Título / Tema de la Encuesta:", placeholder="Ej. Encuesta de Tecnología")
                pub_plat = st.text_input("Plataforma:", placeholder="Ej. AttaPoll, Freecash, Heycash...")
                pub_pago = st.number_input("Pago (€):", min_value=0.10, value=2.50, step=0.10)
                pub_duracion = st.number_input("Duración (minutos):", min_value=1, value=10, step=1)
            
            with col_p2:
                pub_cat = st.selectbox("Categoría:", ["Investigación Académica", "Prueba de Software / UX", "Estudio de Mercado", "Entretenimiento", "Consumo", "Consumo y Entretenimiento", "Política y Sociedad"])
                pub_paises = st.text_input("Países permitidos:", value="España, México, Internacional")
                pub_metodo = st.text_input("Método de cobro:", value="PayPal / Gift Cards")
                pub_confi = st.selectbox("Fiabilidad:", ["Altísimo", "Muy Alto", "Alto", "Medio-Alto", "Medio"])
            
            pub_enlace = st.text_input("🔗 Enlace de Referido / Destino:", placeholder="Déjalo en blanco para usar tu enlace guardado automáticamente de esa plataforma.")
            
            btn_publicar = st.form_submit_button("🚀 Publicar en el Radar", use_container_width=True)
            
            if btn_publicar:
                if pub_titulo and pub_plat:
                    enlace_final = pub_enlace.strip()
                    if enlace_final == "":
                        enlace_guardado = obtener_enlace_afiliado(pub_plat)
                        if enlace_guardado:
                            enlace_final = enlace_guardado
                            st.info(f"💡 Usando automáticamente tu enlace guardado de **{pub_plat}**: {enlace_final}")
                        else:
                            enlace_final = "https://www.google.com"
                            st.warning(f"⚠️ No hay enlace guardado para {pub_plat}. Añade uno la próxima vez para recordarlo.")
                    else:
                        guardar_enlace_afiliado(pub_plat, enlace_final)
                        st.success(f"💾 Nuevo enlace de afiliado guardado para '{pub_plat}'.")

                    publicar_encuesta_db(pub_titulo, pub_plat, pub_pago, pub_duracion, pub_cat, pub_paises, pub_metodo, enlace_final, pub_confi)
                    st.success("¡Oferta publicada correctamente en el Radar!")
                else:
                    st.error("Rellena al menos el Título y la Plataforma.")
                    
    elif clave_admin != "":
        st.error("Clave incorrecta")