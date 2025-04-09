
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, risk_models, expected_returns, plotting

st.set_page_config(page_title="Análisis del Portafolio", layout="wide")
st.markdown('<style>body { font-family: "Times New Roman", serif; }</style>', unsafe_allow_html=True)

if "usuario" not in st.session_state:
    st.warning("Debes completar el formulario en la página de inicio.")
    st.page_link("app_portafolio.py", label="Volver al inicio", icon="🏠")
    st.stop()

user = st.session_state["usuario"]
tickers = [t.strip().upper() for t in user["activos"].split(",")]
inicio = user["inicio"]
fin = user["fin"]
objetivo = user["objetivo"]

st.title(f"📈 Análisis del Portafolio de {user['nombre']}")
st.write(f"Correo: {user['correo']}")
st.write(f"Activos seleccionados: {', '.join(tickers)}")
st.write(f"Periodo: {inicio} a {fin}")
st.write(f"Objetivo de optimización: **{objetivo}**")

@st.cache_data
def obtener_datos(tickers, inicio, fin):
    precios = yf.download(tickers, start=inicio, end=fin)["Close"]
    return precios.dropna()

precios = obtener_datos(tickers, inicio, fin)

returns = precios.pct_change().dropna()
mu = expected_returns.mean_historical_return(precios)
S = risk_models.sample_cov(precios)

ef = EfficientFrontier(mu, S)
if objetivo == "Máximo Sharpe":
    weights = ef.max_sharpe()
else:
    weights = ef.min_volatility()

cleaned_weights = ef.clean_weights()
perf = ef.portfolio_performance(verbose=False)

st.subheader("📊 Pesos Óptimos del Portafolio")
df_weights = pd.DataFrame.from_dict(cleaned_weights, orient='index', columns=["Peso"]).sort_values("Peso", ascending=False)
st.dataframe(df_weights.style.format({"Peso": "{:.2%}"}))

col1, col2, col3 = st.columns(3)
col1.metric("Retorno esperado", f"{perf[0]*100:.2f}%")
col2.metric("Volatilidad", f"{perf[1]*100:.2f}%")
col3.metric("Sharpe Ratio", f"{perf[2]:.2f}")

st.subheader("📉 Asignación de Activos")
fig1, ax1 = plt.subplots()
ax1.pie(df_weights["Peso"], labels=df_weights.index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

st.subheader("🧮 Frontera Eficiente")
ef_plot = EfficientFrontier(mu, S)
fig2, ax2 = plt.subplots()
plotting.plot_efficient_frontier(ef_plot, ax=ax2, show_assets=True)
st.pyplot(fig2)

st.subheader("📈 Rendimiento Acumulado del Portafolio")
weighted_returns = (returns * pd.Series(cleaned_weights)).sum(axis=1)
cumulative_returns = (1 + weighted_returns).cumprod()

fig3, ax3 = plt.subplots()
cumulative_returns.plot(ax=ax3, title="Rendimiento Acumulado")
st.pyplot(fig3)

st.subheader("⚠️ Análisis de Riesgo - VaR")
VaR_95 = np.percentile(weighted_returns, 5)
st.write(f"**VaR al 95% de confianza (1 día): {VaR_95*100:.2f}%**")

st.subheader("🚨 Prueba de Estrés: Simulación de caída del 20% en todos los activos")
stress_prices = precios * 0.8
stress_returns = stress_prices.pct_change().dropna()
stress_mu = expected_returns.mean_historical_return(stress_prices)
stress_S = risk_models.sample_cov(stress_prices)

stress_ef = EfficientFrontier(stress_mu, stress_S)
stress_ef.set_weights(weights)
stress_perf = stress_ef.portfolio_performance(verbose=False)

st.write(f"**Retorno bajo estrés:** {stress_perf[0]*100:.2f}%")
st.write(f"**Volatilidad bajo estrés:** {stress_perf[1]*100:.2f}%")
st.write(f"**Sharpe bajo estrés:** {stress_perf[2]:.2f}")

st.subheader("📤 Descargar archivo de consulta")
resultados = {
    "Nombre": user["nombre"],
    "Correo": user["correo"],
    "Activos": ", ".join(tickers),
    "Fecha inicio": inicio,
    "Fecha fin": fin,
    "Objetivo": objetivo,
    "Retorno esperado": f"{perf[0]*100:.2f}%",
    "Volatilidad": f"{perf[1]*100:.2f}%",
    "Sharpe Ratio": f"{perf[2]:.2f}",
    "VaR 95%": f"{VaR_95*100:.2f}%",
    "Retorno bajo estrés": f"{stress_perf[0]*100:.2f}%",
    "Volatilidad bajo estrés": f"{stress_perf[1]*100:.2f}%",
    "Sharpe bajo estrés": f"{stress_perf[2]:.2f}"
}

df_resultados = pd.DataFrame(resultados.items(), columns=["Descripción", "Valor"])
csv = df_resultados.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar resumen en CSV", data=csv, file_name="resumen_portafolio.csv", mime="text/csv")
