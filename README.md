# 🔍 Automatización del Journal Entry Testing (JET) con IA Híbrida

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![UAX](https://img.shields.io/badge/Máster-Inteligencia_Artificial-black.svg)](https://www.uax.com/)

Este repositorio contiene el código fuente y el entorno de despliegue desarrollados para el **Trabajo de Fin de Máster (TFM)** del Máster Universitario en Inteligencia Artificial de la Universidad Alfonso X el Sabio (UAX).

El proyecto propone una arquitectura tecnológica avanzada orientada a modernizar la detección de fraude contable en la auditoría financiera, garantizando el cumplimiento de la norma **NIA-ES 240** mediante el paradigma de gobernanza *Human-in-the-Loop* (HITL).

---

## 🚀 Arquitectura y Tecnologías Utilizadas

El sistema integra un flujo de trabajo en dos fases que combina el aprendizaje automático no supervisado con la Inteligencia Artificial Generativa:

1. **Motor Analítico (Detección):** Algoritmo `Isolation Forest` para identificar anomalías estadísticas en entornos de clases extremadamente desbalanceadas.
2. **Explicabilidad Matemática (XAI):** `SHAP` (*SHapley Additive exPlanations*) para calcular el peso exacto de cada variable financiera en la alerta de fraude.
3. **Agente Documental (LLM):** `Google Gemini API` orquestado mediante *Prompt Engineering* determinista (temperatura = 0.0) para redactar los papeles de trabajo formales sin alucinaciones.

**Stack Tecnológico:**
* **Lenguaje:** Python
* **Data Science:** `Pandas`, `NumPy`, `Scikit-Learn`
* **Explicabilidad:** `SHAP`
* **Modelos Generativos:** `google-generativeai`
* **Front-end / Interfaz:** `Streamlit`

---

## 📂 Estructura del Repositorio

```text
├── Auditoria_FraudeDetection.ipynb             # Cuadernos Jupyter (Google Colab) con el EDA y entrenamiento inicial.
├── app.py                                      # Código fuente principal del panel interactivo (Frontend y Backend).
├── requirements.txt                            # Lista de dependencias y librerías necesarias.
├── sample_data.csv                             # Muestra de 60 transacciones (PaySim) para pruebas locales con fraudes inyectados.
└── README.md                                   # Documentación principal del proyecto.
````

## ⚙️ Instrucciones de Ejecución Local
Si deseas probar el prototipo interactivo en tu propia máquina, sigue estos pasos en tu terminal:

1. Clonar el repositorio: git clone [https://github.com/paulamainez/TFM-Auditoria-AI.git](https://github.com/paulamainez/TFM-Auditoria-AI.git)
cd TFM-Auditoria-AI

2. Instalar las dependencias requeridas:
pip install -r requirements.txt

3. Configurar la clave API de Google Gemini:
Para que el Agente Documental funcione, necesitas tener una clave API válida de Google Gemini. Puedes insertarla directamente en la interfaz gráfica al iniciar la aplicación o configurarla en tus variables de entorno.

4. Ejecutar la aplicación:
streamlit run app.py

Una vez ejecutado este comando, se abrirá automáticamente una pestaña en tu navegador web local (normalmente en http://localhost:8501) donde podrás interactuar con el panel del auditor, subir el archivo sample_data.csv y analizar las anomalías.

## 🛡️ Consideraciones Normativas y Gobernanza
Este prototipo ha sido diseñado alineándose con los requerimientos de la Norma Internacional de Auditoría (NIA-ES 240) y operando bajo el paradigma Human-in-the-Loop (HITL). La Inteligencia Artificial actúa como un copiloto analítico, pero la decisión final y la responsabilidad probatoria residen inalienablemente en el juicio profesional del auditor humano.

## 👨‍🎓 Autoría y Contexto Académico
Autora: Paula Mainez Herraiz
Tutor: Leonardo Dulccetti
Institución: Universidad Alfonso X el Sabio (UAX)
Fecha: Junio 2026


