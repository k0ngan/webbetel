# ui.py
import streamlit as st

def set_dark_theme():
    dark_css = """
    <style>
    /* Fondo general en modo oscuro */
    body, [data-testid="stAppViewContainer"], .css-1outpf7, .css-hxt7ib {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
    }
    /* Enlaces y textos */
    a, .css-1vbd788, .css-1cpxqw2, .css-18e3th9 {
        color: #81c784 !important;
    }
    /* Títulos del sidebar */
    .css-1cypcdb {
        color: #FFFFFF !important;
    }
    /* Botón de subida de archivo */
    .css-19ih76x {
        background-color: #333 !important;
        color: #FFF !important;
        border: 1px solid #666 !important;
    }
    /* Barra de progreso */
    .stProgress > div > div > div > div {
        background-color: #81c784;
    }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

def main_header():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1rem;">
            <h1 style="color:#81c784;">Dashboard de Recursos Humanos</h1>
            <p>Análisis completo para toma de decisiones estratégicas</p>
        </div>
        """,
        unsafe_allow_html=True
    )
