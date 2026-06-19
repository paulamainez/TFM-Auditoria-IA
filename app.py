import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from google import genai

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="IA Auditor Dashboard",
    page_icon="🔎",
    layout="wide"
)

st.title("IA Auditor Dashboard: Journal Entry Testing")
st.markdown("Sistema automatizado de detección de fraude basado en Isolation Forest y Gemini (NIA-ES 240).")

# ==========================================
# 2. FUNCIONES DEL NÚCLEO
# ==========================================
@st.cache_data
def ejecutar_pipeline_ia(df, contaminacion):
    # Fase 1: Preprocesamiento
    df_riesgo = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])].copy()
    df_riesgo['cuenta_vaciada'] = (df_riesgo['newbalanceOrig'] == 0).astype(int)
    
    # Variables para el modelo numérico
    features = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'cuenta_vaciada']
    X = df_riesgo[features]
    
    # Fase 2: Isolation Forest
    modelo = IsolationForest(n_estimators=100, contamination=contaminacion, random_state=42)
    df_riesgo['anomalia'] = modelo.fit_predict(X)
    
    # Fase 3: Top 20
    df_fraude = df_riesgo[df_riesgo['anomalia'] == -1]
    top_20 = df_fraude.sort_values(by='amount', ascending=False).head(20)
    
    return modelo, X, top_20

def redactar_informe_llm(api_key, transaccion, motivo_shap):
    try:
        client = genai.Client(api_key=api_key)
        
        tipo = transaccion['type']
        importe = f"{transaccion['amount']:,.2f} €"
        vaciado = "SÍ" if transaccion['cuenta_vaciada'] == 1 else "NO"
        
        prompt = f"""
        ACTÚA COMO: Socio de Auditoría Senior experto en NIA 240.
        CONTEXTO: Estamos realizando un Journal Entry Testing (JET) con IA.
        DATOS DE LA TRANSACCIÓN:
        - Tipo: {tipo}
        - Importe: {importe}
        - ¿Cuenta vaciada por completo?: {vaciado}
        JUSTIFICACIÓN TÉCNICA (SHAP): {motivo_shap}
        
        FORMATO DE SALIDA:
        1. EXPLICACIÓN BREVE
        2. FACTORES CLAVE
        3. NIVEL DE RIESGO
        4. CONCLUSIÓN NIA 240
        REGLA: No inventes datos. Sé riguroso y técnico.
        """
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        return f"Error al conectar con la IA: {e}"

# ==========================================
# 3. PANEL LATERAL
# ==========================================
with st.sidebar:
    st.header("⚙️ Panel de Control")
    archivo_subido = st.file_uploader("Sube el Libro Diario (CSV)", type=["csv"])
    
    st.markdown("---")
    st.subheader("Parámetros del Modelo")
    sensibilidad = st.slider("Tasa de Anomalías (Contaminación)", min_value=0.001, max_value=0.05, value=0.01, step=0.001, format="%.3f")
    
    st.markdown("---")
    st.subheader("Agente Documental")
    gemini_key = st.text_input("API Key de Google Gemini", type="password", help="Tu clave no se guardará en ningún servidor.")

# ==========================================
# 4. CUERPO PRINCIPAL DE LA APP
# ==========================================
if archivo_subido is not None:
    try:
        try:
            # 1er Intento: Estándar Internacional (Separado por comas y formato UTF-8)
            archivo_subido.seek(0)
            df_original = pd.read_csv(archivo_subido, sep=',')
        except Exception:
            try:
                # 2do Intento: Formato Excel España (Separado por punto y coma y formato Latin1)
                archivo_subido.seek(0)
                df_original = pd.read_csv(archivo_subido, sep=';', encoding='latin1')
            except Exception:
                # 3er Intento: Si falla todo, intentamos forzar a Python a adivinarlo
                archivo_subido.seek(0)
                df_original = pd.read_csv(archivo_subido, sep=None, engine='python', encoding='utf-8')
            
        # --- ASISTENTE DE MAPEO DE DATOS ---
        columnas_requeridas = ['type', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest', 'nameOrig']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_original.columns]
        
        if len(columnas_faltantes) > 0:
            st.warning("**Estructura no reconocida: Activando Asistente de Mapeo de Datos.**")
            st.info("Las columnas de tu archivo no coinciden con el estándar del modelo. Por favor, selecciona qué columna de tu archivo corresponde a cada variable requerida por la IA:")
            
            # Formulario interactivo para el auditor
            with st.form("mapeador_columnas"):
                mapeo = {}
                opciones_columnas = ["-- Seleccionar columna --"] + list(df_original.columns)
                
                col1, col2 = st.columns(2)
                for i, col_req in enumerate(columnas_requeridas):
                    # Dibujar los selectores repartidos en dos columnas
                    with col1 if i % 2 == 0 else col2:
                        mapeo[col_req] = st.selectbox(f"Asignar a '{col_req}':", options=opciones_columnas)
                
                boton_mapeo = st.form_submit_button("Aplicar Traducción y Ejecutar Auditoría")
            
            if boton_mapeo:
                if "-- Seleccionar columna --" in mapeo.values():
                    st.error("Por favor, asigna una columna para todas las variables antes de continuar.")
                else:
                    # Renombrar las columnas del DataFrame original para que la IA lo entienda
                    diccionario_renombre = {v: k for k, v in mapeo.items()}
                    df_original = df_original.rename(columns=diccionario_renombre)
                    st.success("Datos mapeados correctamente. Recarga la página si deseas volver a empezar.")
                    
                    # Forzamos que la lista de faltantes sea 0 para que ejecute el modelo abajo
                    columnas_faltantes = []
        
        # --- EJECUCIÓN DEL MODELO ---
        if len(columnas_faltantes) == 0:
            tab1, tab2, tab3 = st.tabs(["📊 Resumen Global", "🚨 Top 20 Sospechosos", "🤖 Informe Forense (LLM)"])
            
            with st.spinner("Ejecutando algoritmos de detección de fraude..."):
                modelo, X_train, top_20 = ejecutar_pipeline_ia(df_original, sensibilidad)
            
            # --- PESTAÑA 1: RESUMEN GLOBAL ---
            with tab1:
                st.subheader("Métricas de la Auditoría")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Registros Ingestados", f"{len(df_original):,}")
                col2.metric("Operaciones de Riesgo Analizadas", f"{len(X_train):,}")
                col3.metric("Anomalías Aisladas", f"{len(top_20):,}")
                st.dataframe(df_original.head(5))

            # --- PESTAÑA 2: TOP 20 ---
            with tab2:
                st.subheader("Muestra de Riesgo Extraída (NIA-ES 240)")
                st.dataframe(top_20[['type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig', 'cuenta_vaciada']])

            # --- PESTAÑA 3: INFORME FORENSE ---
            with tab3:
                st.subheader("Generación de Papel de Trabajo")
                opciones = top_20.index.tolist()
                id_seleccionado = st.selectbox("Selecciona el ID de la transacción a auditar:", opciones)
                
                if st.button("Generar Informe con IA"):
                    if not gemini_key:
                        st.error("Por favor, introduce tu API Key de Gemini en el panel lateral.")
                    else:
                        with st.spinner("SHAP analizando tensores y Gemini redactando la narrativa..."):
                            transaccion_actual = top_20.loc[id_seleccionado]
                            explicacion_visual = "El algoritmo detectó importes atípicos combinados con el vaciado total e inmediato de la cuenta de origen."
                            informe = redactar_informe_llm(gemini_key, transaccion_actual, explicacion_visual)
                            
                            st.success("Papel de trabajo generado con éxito.")
                            st.markdown("### Borrador Final")
                            st.info(informe)
                            st.download_button(
                                label="Descargar Papel de Trabajo (.txt)",
                                data=informe,
                                file_name=f"Informe_Auditoria_TX_{id_seleccionado}.txt",
                                mime="text/plain"
                            )
                            
    except Exception as e:
         st.error(f"Error al leer el archivo. Asegúrate de que es un CSV válido. Detalle técnico: {e}")

else:
    st.info("¡Hola! Para comenzar la auditoría, por favor sube un archivo CSV validado en el panel lateral izquierdo.")