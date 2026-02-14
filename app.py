import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- CONFIGURACIÓN ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS_FILE = 'credenciales.json'
SHEET_NAME = 'base de datos'  
TAB_NAME = 'Clientes'         

# --- USUARIOS (Contraseña 1234) ---
USUARIOS = {
    # ADMIN
    "alfacreditenrique@gmail.com": {"password": "1234", "sucursal": "ADMINISTRADOR", "rol": "admin"},
    # GERENTES
    "gerenteesteli7@gmail.com": {"password": "1234", "sucursal": "Sucursal Esteli", "rol": "gerente"},
    "gerentemasaya25@gmail.com": {"password": "1234", "sucursal": "Sucursal Masaya", "rol": "gerente"},
    "gerenterivas1@gmail.com": {"password": "1234", "sucursal": "Sucursal Rivas", "rol": "gerente"},
    "gerentejinotepe@gmail.com": {"password": "1234", "sucursal": "Sucursal Jinotepe", "rol": "gerente"},
    "gerentemanaguanorte@gmail.com": {"password": "1234", "sucursal": "Sucursal Managua Norte", "rol": "gerente"},
    "gerentejuigalpa@gmail.com": {"password": "1234", "sucursal": "Sucursal Juigalpa", "rol": "gerente"},
    "gerentemanaguabolonia@gmail.com": {"password": "1234", "sucursal": "Sucursal Managua Bolonia", "rol": "gerente"},
    "gerentesebaco@gmail.com": {"password": "1234", "sucursal": "Sucursal Sebaco", "rol": "gerente"},
    "gerenteleon8@gmail.com": {"password": "1234", "sucursal": "Sucursal León", "rol": "gerente"},
}

# --- FUNCIONES ---

def conectar_google_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
    return sheet

def cargar_datos(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def guardar_cambios(sheet, df_editado):
    st.info("Sincronizando con Google Sheets...")
    errores = 0
    
    # Iteramos sobre el dataframe. 'i' será el índice original (ej. 10, 25, etc.)
    for i, row in df_editado.iterrows():
        # CORRECCIÓN DEL ERROR "INDEX OUT OF BOUNDS":
        # La fila en Excel es simplemente el índice + 2 (porque índice 0 es fila 2 en Excel)
        row_num = i + 2
        
        try:
            # Recuperamos los valores de forma segura (por si el nombre cambia un poco)
            val_status = row.get('Status', '')
            val_justif = row.get('Justificacion', row.get('Justificación', '')) # Prueba con y sin acento
            val_asig = row.get('Asignado_Colaborador', '')
            val_monto = row.get('Monto desembolsar', row.get('Monto Desembolsar', ''))
            
            # Actualizamos las celdas (Columnas K, L, M, N)
            # Verifica que estos números coincidan con tus columnas en Excel:
            sheet.update_cell(row_num, 11, val_status)  # Col K (11)
            sheet.update_cell(row_num, 12, val_justif)  # Col L (12)
            sheet.update_cell(row_num, 13, val_asig)    # Col M (13)
            sheet.update_cell(row_num, 14, val_monto)   # Col N (14)
            
            # Fecha Actualización (Col O -> 15)
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sheet.update_cell(row_num, 15, fecha_actual)
            
        except Exception as e:
            errores += 1
            st.error(f"Error en fila {row_num}: {e}")
            
    if errores == 0:
        st.success("¡Datos actualizados correctamente!")
    else:
        st.warning(f"Se completó el proceso con {errores} errores. Revisa los mensajes arriba.")

# --- INTERFAZ ---

st.set_page_config(page_title="Gestión de Créditos", layout="wide")
st.title("Sistema de Gestión de Créditos")

# 1. LOGIN
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

if not st.session_state['logueado']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.subheader("Acceso Restringido")
            usuario = st.text_input("Correo")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                usuario = usuario.strip().lower() 
                if usuario in USUARIOS and USUARIOS[usuario]["password"] == password:
                    st.session_state['logueado'] = True
                    st.session_state['usuario_actual'] = usuario
                    st.session_state['datos_usuario'] = USUARIOS[usuario]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

# 2. APLICACIÓN PRINCIPAL
else:
    user_email = st.session_state['usuario_actual']
    user_data = st.session_state['datos_usuario']
    es_admin = user_data['rol'] == 'admin'
    
    st.sidebar.markdown(f"**Usuario:** {user_email}")
    st.sidebar.markdown(f"**Rol:** {user_data['sucursal']}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['logueado'] = False
        st.rerun()

    try:
        sheet = conectar_google_sheet()
        df = cargar_datos(sheet)
        
        # --- FILTRADO ---
        if es_admin:
            st.info("Modo Administrador: Viendo todos los registros.")
            filtro_sucursal = st.selectbox("Filtrar por Sucursal", ["Todas"] + list(df['Sucursal'].unique()))
            if filtro_sucursal != "Todas":
                df_filtrado = df[df['Sucursal'] == filtro_sucursal].copy()
            else:
                df_filtrado = df.copy()
        else:
            # Filtramos por Email_Gerente
            if 'Email_Gerente' in df.columns:
                df_filtrado = df[df['Email_Gerente'] == user_email].copy()
            else:
                st.error("⚠️ Error Crítico: No encuentro la columna 'Email_Gerente' en tu Excel.")
                st.stop()

        if not df_filtrado.empty:
            # Configuración de columnas
            column_config = {
                "Email_Gerente": st.column_config.TextColumn(disabled=True),
                "Sucursal": st.column_config.TextColumn(disabled=True),
                "Monto Solicitado": st.column_config.TextColumn(disabled=True), 
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Proceso", "Denegado", "Desembolsado", "Pendiente"],
                    required=True
                ),
                "Monto desembolsar": st.column_config.NumberColumn("Monto Desembolso")
            }

            st.write(f"Mostrando {len(df_filtrado)} registros.")
            
            df_editado = st.data_editor(
                df_filtrado,
                column_config=column_config,
                num_rows="fixed",
                hide_index=True,
                use_container_width=True,
                height=500
            )
            
            if st.button("Guardar Cambios"):
                if not df_editado.equals(df_filtrado):
                    guardar_cambios(sheet, df_editado) # Ya no necesitamos indices_originales
                    st.rerun()
                else:
                    st.info("No hay cambios pendientes.")
        else:
            st.warning("No tienes clientes asignados actualmente.")

    except Exception as e:
        st.error(f"Error general: {e}")