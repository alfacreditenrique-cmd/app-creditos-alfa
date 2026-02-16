import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA (DEBE IR AL PRINCIPIO) ---
st.set_page_config(
    page_title="AlfaCredit S.A. - Gestión",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (CSS) ---
# Aquí definimos el diseño "AlfaCredit Dark Mode"
st.markdown("""
    <style>
    /* 1. Fondo Principal Negro Puro */
    .stApp {
        background-color: #000000;
    }
    
    /* 2. Barra Lateral (Gris muy oscuro para contraste) */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #333;
    }

    /* 3. Títulos y Encabezados en Verde AlfaCredit */
    h1, h2, h3, h4 {
        color: #2ecc71 !important; /* Verde Esmeralda Vibrante */
        font-family: 'Arial', sans-serif;
    }

    /* 4. Textos Generales en Blanco */
    p, label, span, div {
        color: #e0e0e0;
    }

    /* 5. Métricas (KPIs) */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #2ecc71 !important; /* Etiqueta verde */
    }
    [data-testid="stMetricDelta"] {
        color: #cccccc !important;
    }

    /* 6. Botones (Verdes con texto blanco) */
    div.stButton > button:first-child {
        background-color: #27ae60;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #2ecc71; /* Verde más claro al pasar mouse */
        box-shadow: 0 0 10px #2ecc71;
    }

    /* 7. Inputs y Tablas */
    .stTextInput > div > div > input {
        color: white;
        background-color: #1e1e1e;
        border: 1px solid #444;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN GOOGLE ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS_FILE = 'credenciales.json'
SHEET_NAME = 'base de datos'
TAB_NAME = 'Clientes'

# --- USUARIOS ---
# He corregido el patrón de contraseñas para evitar errores de acceso
USUARIOS = {
    "alfacreditenrique@gmail.com": {"password": "Matriz,_2025", "sucursal": "ADMINISTRADOR", "rol": "admin"},
    "gerenteesteli7@gmail.com": {"password": "gerenteesteli7@gerenteesteli7", "sucursal": "Sucursal Esteli", "rol": "gerente"},
    "gerentemasaya25@gmail.com": {"password": "gerentemasaya25@gerentemasaya25", "sucursal": "Sucursal Masaya", "rol": "gerente"},
    "gerenterivas1@gmail.com": {"password": "gerenterivas1@gerenterivas1", "sucursal": "Sucursal Rivas", "rol": "gerente"},
    "gerentejinotepe@gmail.com": {"password": "gerentejinotepe@gerentejinotepe", "sucursal": "Sucursal Jinotepe", "rol": "gerente"},
    "gerentemanaguanorte@gmail.com": {"password": "gerentemanaguanorte@gerentemanaguanorte", "sucursal": "Sucursal Managua Norte", "rol": "gerente"},
    "gerentejuigalpa@gmail.com": {"password": "gerentejuigalpa@gerentejuigalpa", "sucursal": "Sucursal Juigalpa", "rol": "gerente"},
    "gerentemanaguabolonia@gmail.com": {"password": "gerentemanaguabolonia@gerentemanaguabolonia", "sucursal": "Sucursal Managua Bolonia", "rol": "gerente"},
    "gerentesebaco@gmail.com": {"password": "gerentesebaco@gerentesebaco", "sucursal": "Sucursal Sebaco", "rol": "gerente"},
    "gerenteleon8@gmail.com": {"password": "gerenteleon8@gerenteleon8", "sucursal": "Sucursal León", "rol": "gerente"},
}

# --- FUNCIONES ---

def conectar_google_sheet():
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
            
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

def cargar_datos(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def limpiar_moneda(valor):
    if isinstance(valor, str):
        limpio = valor.replace('C$', '').replace(',', '').strip()
        if limpio == '': return 0.0
        try:
            return float(limpio)
        except:
            return 0.0
    return float(valor or 0)

def guardar_cambios(sheet, df_editado, es_admin):
    with st.spinner('🔄 Sincronizando con base de datos AlfaCredit...'):
        errores = 0
        for i, row in df_editado.iterrows():
            row_num = i + 2
            try:
                # 1. ACTUALIZACIÓN ESTÁNDAR
                sheet.update_cell(row_num, 11, row.get('Status', ''))  
                sheet.update_cell(row_num, 12, row.get('Justificacion', row.get('Justificación', '')))  
                sheet.update_cell(row_num, 13, row.get('Asignado_Colaborador', ''))    
                sheet.update_cell(row_num, 14, row.get('Monto desembolsar', row.get('Monto Desembolsar', '')))   
                
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                sheet.update_cell(row_num, 15, fecha_actual)

                # 2. ACTUALIZACIÓN ADMIN
                if es_admin:
                    sheet.update_cell(row_num, 1, row.get('Agente Call Center', ''))
                    sheet.update_cell(row_num, 2, row.get('Fecha Reporte', ''))
                    sheet.update_cell(row_num, 3, row.get('Nombre_Completo', ''))
                    sheet.update_cell(row_num, 4, row.get('Tipo de credito', ''))
                    sheet.update_cell(row_num, 5, row.get('Telefono', ''))
                    sheet.update_cell(row_num, 6, row.get('Direccion_Negocio', ''))
                    sheet.update_cell(row_num, 7, row.get('Tipo_Negocio', ''))
                    sheet.update_cell(row_num, 10, row.get('Monto Solicitado', ''))
                
            except Exception as e:
                errores += 1
                st.error(f"Error en fila {row_num}: {e}")
                
        if errores == 0:
            st.success("✅ ¡Datos actualizados correctamente!")
            st.rerun()
        else:
            st.warning(f"⚠️ Se completó con {errores} errores.")

# --- INTERFAZ ---

# 1. LOGIN
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

if not st.session_state['logueado']:
    # Diseño de Login Centrado y Bonito
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #2ecc71;'>AlfaCredit S.A.</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: white;'>Sistema de Gestión de Créditos</h4>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("📧 Correo Institucional")
            password = st.text_input("🔑 Contraseña", type="password")
            submit = st.form_submit_button("INGRESAR AL SISTEMA")
            
            if submit:
                usuario = usuario.strip().lower() 
                if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
                    st.session_state['logueado'] = True
                    st.session_state['usuario_actual'] = usuario
                    st.session_state['datos_usuario'] = USUARIOS[usuario]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")

# 2. PANEL PRINCIPAL
else:
    user_email = st.session_state['usuario_actual']
    user_data = st.session_state['datos_usuario']
    es_admin = user_data['rol'] == 'admin'
    
    # --- BARRA LATERAL CON LOGO ---
    with st.sidebar:
        # Intentamos mostrar el logo si existe
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            # Placeholder elegante si no hay logo aun
            st.markdown("<h1 style='color: #2ecc71;'>ALFACREDIT</h1>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.write(f"👤 **Usuario:** {user_data['sucursal']}")
        st.write(f"📧 **Correo:** {user_email}")
        st.markdown("---")
        if st.button("🔒 Cerrar Sesión"):
            st.session_state['logueado'] = False
            st.rerun()

    # --- CONTENIDO PRINCIPAL ---
    st.title("📊 Dashboard de Créditos")
    st.markdown(f"Bienvenido, **{user_data['sucursal']}**")

    try:
        sheet = conectar_google_sheet()
        df = cargar_datos(sheet)
        
        # --- FILTRADO ---
        if es_admin:
            st.success("🛡️ Modo Administrador Activo")
            filtro_sucursal = st.selectbox("Filtrar por Sucursal", ["Todas"] + list(df['Sucursal'].unique()))
            if filtro_sucursal != "Todas":
                df_filtrado = df[df['Sucursal'] == filtro_sucursal].copy()
            else:
                df_filtrado = df.copy()
        else:
            if 'Email_Gerente' in df.columns:
                df_filtrado = df[df['Email_Gerente'] == user_email].copy()
            else:
                st.error("⚠️ Error: No encuentro la columna 'Email_Gerente'.")
                st.stop()

        if not df_filtrado.empty:
            
            # Corrección Teléfono
            if 'Telefono' in df_filtrado.columns:
                df_filtrado['Telefono'] = df_filtrado['Telefono'].astype(str)
            
            # --- KPI & GRÁFICAS ---
            col_monto = 'Monto desembolsar' if 'Monto desembolsar' in df_filtrado.columns else 'Monto Desembolsar'
            df_filtrado['Monto_Num'] = df_filtrado[col_monto].apply(limpiar_moneda)
            
            total_clientes = len(df_filtrado)
            total_dinero = df_filtrado['Monto_Num'].sum()
            conteo_status = df_filtrado['Status'].value_counts().reset_index()
            conteo_status.columns = ['Estado', 'Cantidad']
            
            # Diseño de Tarjetas KPI
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("📂 Clientes Totales", total_clientes)
            kpi2.metric("💰 Dinero Desembolsado", f"C$ {total_dinero:,.2f}")
            
            desembolsados = len(df_filtrado[df_filtrado['Status'] == 'Desembolsado'])
            tasa = (desembolsados / total_clientes * 100) if total_clientes > 0 else 0
            kpi3.metric("📈 Tasa de Aprobación", f"{tasa:.1f}%")
            
            st.markdown("---")
            
            # Gráficos con tema oscuro
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Distribución por Estado")
                fig_pie = px.pie(
                    conteo_status, 
                    values='Cantidad', 
                    names='Estado', 
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Greens_r # Verdes
                )
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with g2:
                st.subheader("Cantidad de Clientes")
                fig_bar = px.bar(
                    conteo_status, 
                    x='Estado', 
                    y='Cantidad', 
                    color='Estado',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")
            st.subheader("📝 Gestión de Clientes")

            # --- CONFIGURACIÓN DE TABLA ---
            column_config = {
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Proceso", "Denegado", "Desembolsado", "Pendiente"],
                    required=True
                ),
                "Monto desembolsar": st.column_config.NumberColumn("Monto Desembolso", format="C$ %.2f")
            }

            cols_bloqueadas_gerente = [
                "Agente Call Center", "Fecha Reporte", "Nombre_Completo", 
                "Tipo de credito", "Telefono", "Direccion_Negocio", 
                "Tipo_Negocio", "Email_Gerente", "Sucursal", "Monto Solicitado"
            ]

            estado_bloqueo = False if es_admin else True

            for col in cols_bloqueadas_gerente:
                column_config[col] = st.column_config.TextColumn(disabled=estado_bloqueo)

            df_editado = st.data_editor(
                df_filtrado,
                column_config=column_config,
                num_rows="fixed",
                hide_index=True,
                use_container_width=True,
                height=500
            )
            
            col_btn, _ = st.columns([1, 4])
            with col_btn:
                if st.button("💾 GUARDAR CAMBIOS", type="primary"):
                    if not df_editado.equals(df_filtrado):
                        guardar_cambios(sheet, df_editado, es_admin)
                    else:
                        st.info("No hay cambios pendientes.")
        else:
            st.warning("📭 No tienes clientes asignados actualmente.")

    except Exception as e:
        st.error(f"Error del sistema: {e}")
