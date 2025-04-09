
import streamlit as st
import os
from datetime import date

# Configuración de estilo
st.set_page_config(page_title="Finanzas | Móviles", layout="centered")

st.markdown("""
    <style>
    body {
        background-color: white;
        font-family: "Times New Roman", serif;
    }
    .centered {
        display: flex;
        justify-content: center;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# === Portada con imagen ===
st.markdown('<div class="centered"><img src="logo.png" width="300"></div>', unsafe_allow_html=True)

st.title("Bienvenido a Finanzas | Móviles 📊")
st.subheader("Optimiza tu portafolio en segundos")

# === Registro de usuario ===
with st.form("form_inicio"):
    st.write("### Ingresa tu información:")
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo Electrónico")
    
    st.write("### Selección de activos:")
    tipo = st.selectbox("Tipo de instrumento", ["Acciones", "ETFs", "Criptomonedas"])
    activos = st.text_input("Tickers (Yahoo Finance, separados por coma)", value="AAPL, MSFT, GOOGL, AMZN, TSLA")

    st.write("### Selección de periodo:")
    fecha_inicio = st.date_input("Fecha de inicio", value=date(2019, 1, 1))
    fecha_fin = st.date_input("Fecha de fin", value=date.today())

    st.write("### Parámetros de optimización:")
    objetivo = st.radio("Objetivo", ["Máximo Sharpe", "Mínima Varianza"])
    
    submit = st.form_submit_button("Continuar al Análisis")

if submit:
    st.session_state["usuario"] = {
        "nombre": nombre,
        "correo": correo,
        "tipo": tipo,
        "activos": activos,
        "inicio": fecha_inicio.strftime("%Y-%m-%d"),
        "fin": fecha_fin.strftime("%Y-%m-%d"),
        "objetivo": objetivo
    }
    st.success("Datos guardados. Dirígete a la siguiente página para iniciar el análisis.")
    st.page_link("app_datos.py", label="Ir al análisis", icon="📈")
