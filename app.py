import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AlfaCredit S.A.",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (CSS MODO OSCURO) ---
st.markdown("""
    <style>
    /* Fondo y Textos */
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
    h1, h2, h3, h4 { color: #2ecc71 !important; font-family: 'Arial', sans-serif; }
    p, label, span, div { color: #e0e0e0; }
    
    /* Métricas */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #2ecc71 !important; }
    
    /* Botones */
    div.stButton > button:first-child {
        background-color: #27ae60; color: white; border-radius: 8px; border: none; font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #2ecc71; box-shadow: 0 0 10px #2ecc71;
    }
    
    /* Radio Button (Menú) */
    .stRadio > div { flex-direction: column; }
    .stRadio > label { color: white !important; font-weight: bold; }
    
    /* Tablas */
    [data-testid="stDataFrame"] { border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN GOOGLE ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS_FILE = 'credenciales.json'
SHEET_NAME = 'base de datos'
TAB_CLIENTES = 'Clientes'
TAB_HISTORICO = 'Historico' 

# --- USUARIOS ---
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

def conectar_google_sheet(nombre_pestaña):
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
            
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(nombre_pestaña)
        return sheet
    except Exception as e:
        st.error(f"Error de conexión con la hoja '{nombre_pestaña}': {e}")
        st.stop()

def cargar_datos(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df.astype(str)

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
                # Actualización Estándar
                sheet.update_cell(row_num, 11, row.get('Status', ''))  
                sheet.update_cell(row_num, 12, row.get('Justificacion', row.get('Justificación', '')))  
                sheet.update_cell(row_num, 13, row.get('Asignado_Colaborador', ''))    
                sheet.update_cell(row_num, 14, row.get('Monto desembolsar', row.get('Monto Desembolsar', '')))   
                
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                sheet.update_cell(row_num, 15, fecha_actual)

                # Actualización Admin
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

if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

# 1. LOGIN
if not st.session_state['logueado']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #2ecc71;'>AlfaCredit S.A.</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: white;'>Sistema de Gestión</h4>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("📧 Correo Institucional")
            password = st.text_input("🔑 Contraseña", type="password")
            submit = st.form_submit_button("INGRESAR")
            
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
    
    # --- BARRA LATERAL ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.markdown("<h1 style='color: #2ecc71;'>ALFACREDIT</h1>", unsafe_allow_html=True)
            
        st.write(f"👤 **{user_data['sucursal']}**")
        st.markdown("---")
        
        # MENÚ DE NAVEGACIÓN
        menu_seleccion = st.radio("📍 Navegación", ["Gestión Activa", "Histórico de Clientes"])
        
        st.markdown("---")
        if st.button("🔒 Cerrar Sesión"):
            st.session_state['logueado'] = False
            st.rerun()

    # --- LÓGICA DE PÁGINAS ---
    
    # ---------------------------------------------------------
    # PÁGINA 1: GESTIÓN ACTIVA (EDITABLE)
    # ---------------------------------------------------------
    if menu_seleccion == "Gestión Activa":
        st.title("📊 Gestión del Día")
        
        try:
            sheet = conectar_google_sheet(TAB_CLIENTES)
            df = cargar_datos(sheet)
            
            # FILTRADO
            if es_admin:
                st.success("🛡️ Modo Administrador")
                filtro_sucursal = st.selectbox("Filtrar por Sucursal", ["Todas"] + list(df['Sucursal'].unique()))
                df_filtrado = df[df['Sucursal'] == filtro_sucursal].copy() if filtro_sucursal != "Todas" else df.copy()
            else:
                if 'Email_Gerente' in df.columns:
                    df_filtrado = df[df['Email_Gerente'] == user_email].copy()
                else:
                    st.error("Error: Columna Email_Gerente no encontrada.")
                    st.stop()

            if not df_filtrado.empty:
                # 1. CÁLCULOS KPI
                col_monto = 'Monto desembolsar' if 'Monto desembolsar' in df_filtrado.columns else 'Monto Desembolsar'
                df_filtrado['Monto_Num'] = df_filtrado[col_monto].apply(limpiar_moneda)
                
                total_clientes = len(df_filtrado)
                total_dinero = df_filtrado['Monto_Num'].sum()
                desembolsados = len(df_filtrado[df_filtrado['Status'] == 'Desembolsado'])
                tasa = (desembolsados / total_clientes * 100) if total_clientes > 0 else 0
                
                # 2. MOSTRAR KPIs
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Clientes Activos", total_clientes)
                kpi2.metric("Monto Desembolsado", f"C$ {total_dinero:,.2f}")
                kpi3.metric("Efectividad", f"{tasa:.1f}%")
                
                st.markdown("---")
                
                # 3. GRÁFICOS
                g1, g2 = st.columns(2)
                conteo_status = df_filtrado['Status'].value_counts().reset_index()
                conteo_status.columns = ['Estado', 'Cantidad']
                
                with g1:
                    st.subheader("Distribución")
                    fig_pie = px.pie(conteo_status, values='Cantidad', names='Estado', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)
                with g2:
                    st.subheader("Cantidad")
                    fig_bar = px.bar(conteo_status, x='Estado', y='Cantidad', color='Estado', color_discrete_sequence=px.colors.sequential.Greens_r)
                    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown("---")
                st.subheader("📝 Edición de Datos")
                
                # 4. TABLA EDITABLE
                column_config = {
                    "Status": st.column_config.SelectboxColumn("Status", options=["Proceso", "Denegado", "Desembolsado", "Pendiente"], required=True),
                    "Monto desembolsar": st.column_config.NumberColumn("Monto Desembolso", format="C$ %.2f")
                }
                cols_bloqueadas = ["Agente Call Center", "Fecha Reporte", "Nombre_Completo", "Tipo de credito", "Telefono", "Direccion_Negocio", "Tipo_Negocio", "Email_Gerente", "Sucursal", "Monto Solicitado"]
                bloqueo = False if es_admin else True
                for col in cols_bloqueadas:
                    column_config[col] = st.column_config.TextColumn(disabled=bloqueo)

                df_editado = st.data_editor(df_filtrado, column_config=column_config, num_rows="fixed", hide_index=True, use_container_width=True, height=500)
                
                if st.button("💾 GUARDAR CAMBIOS", type="primary"):
                    if not df_editado.equals(df_filtrado):
                        guardar_cambios(sheet, df_editado, es_admin)
                    else:
                        st.info("No hay cambios.")
            else:
                st.warning("No tienes clientes activos.")

        except Exception as e:
            st.error(f"Error: {e}")

    # ---------------------------------------------------------
    # PÁGINA 2: HISTÓRICO (SOLO LECTURA + GRÁFICOS)
    # ---------------------------------------------------------
    elif menu_seleccion == "Histórico de Clientes":
        st.title("📂 Histórico de Operaciones")
        st.markdown("Consulta de registros antiguos. **(Modo Solo Lectura)**")
        
        try:
            sheet_hist = conectar_google_sheet(TAB_HISTORICO)
            df_hist = cargar_datos(sheet_hist)
            
            # FILTRADO HISTÓRICO
            if es_admin:
                # Verificamos si existe la columna Sucursal antes de intentar filtrar
                if 'Sucursal' in df_hist.columns:
                    sucursales_hist = ["Todas"] + list(df_hist['Sucursal'].unique())
                    filtro_hist = st.selectbox("Filtrar Histórico por Sucursal", sucursales_hist)
                    df_view = df_hist[df_hist['Sucursal'] == filtro_hist] if filtro_hist != "Todas" else df_hist
                else:
                    st.warning("El Histórico no tiene columna 'Sucursal'. Se muestran todos los datos.")
                    df_view = df_hist
            else:
                if 'Email_Gerente' in df_hist.columns:
                    df_view = df_hist[df_hist['Email_Gerente'] == user_email]
                else:
                    st.error("El Histórico no tiene columna 'Email_Gerente' para filtrar.")
                    df_view = pd.DataFrame()

            if not df_view.empty:
                # --- AQUÍ AGREGAMOS LOS GRÁFICOS AL HISTÓRICO ---
                
                # 1. CÁLCULOS KPI (Igual que en activa)
                col_monto_hist = 'Monto desembolsar' if 'Monto desembolsar' in df_view.columns else 'Monto Desembolsar'
                
                # Verificamos si existe la columna de montos antes de calcular
                if col_monto_hist in df_view.columns:
                    df_view['Monto_Num'] = df_view[col_monto_hist].apply(limpiar_moneda)
                    total_dinero_hist = df_view['Monto_Num'].sum()
                else:
                    total_dinero_hist = 0

                total_clientes_hist = len(df_view)
                
                if 'Status' in df_view.columns:
                    desembolsados_hist = len(df_view[df_view['Status'] == 'Desembolsado'])
                    tasa_hist = (desembolsados_hist / total_clientes_hist * 100) if total_clientes_hist > 0 else 0
                else:
                    tasa_hist = 0

                # 2. MOSTRAR KPIs
                kpi_h1, kpi_h2, kpi_h3 = st.columns(3)
                kpi_h1.metric("Total Histórico", total_clientes_hist)
                kpi_h2.metric("Monto Histórico", f"C$ {total_dinero_hist:,.2f}")
                kpi_h3.metric("Tasa Global", f"{tasa_hist:.1f}%")
                
                st.markdown("---")

                # 3. GRÁFICOS
                if 'Status' in df_view.columns:
                    g_h1, g_h2 = st.columns(2)
                    conteo_status_hist = df_view['Status'].value_counts().reset_index()
                    conteo_status_hist.columns = ['Estado', 'Cantidad']
                    
                    with g_h1:
                        st.subheader("Distribución Histórica")
                        fig_pie_h = px.pie(conteo_status_hist, values='Cantidad', names='Estado', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
                        fig_pie_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig_pie_h, use_container_width=True)
                    with g_h2:
                        st.subheader("Volumen por Estado")
                        fig_bar_h = px.bar(conteo_status_hist, x='Estado', y='Cantidad', color='Estado', color_discrete_sequence=px.colors.sequential.Greens_r)
                        fig_bar_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig_bar_h, use_container_width=True)

                st.markdown("---")
                
                # 4. TABLA DE BÚSQUEDA (SOLO LECTURA)
                st.subheader("🔍 Detalle de Registros")
                busqueda = st.text_input("Buscar en histórico...", "")
                
                if busqueda:
                    mask = df_view.apply(lambda x: x.astype(str).str.contains(busqueda, case=False).any(), axis=1)
                    df_final = df_view[mask]
                else:
                    df_final = df_view

                st.dataframe(
                    df_final, 
                    use_container_width=True, 
                    hide_index=True,
                    height=600
                )
            else:
                st.warning("No se encontraron registros en el histórico.")
                
        except Exception as e:
            st.error(f"Error cargando histórico: {e}")
