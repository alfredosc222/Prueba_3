"""
Punto de entrada para la herramienta de evaluación de nivel de CBS.
Este archivo es el "orquestador" que importa y llama a la lógica modularizada.
"""
import streamlit as st

from app_state import EvaluationState
from theme_1 import theme_1

# Se importa la función principal de renderizado desde el nuevo módulo de vistas
from modulos.evaluacion_madurez.data_model import load_questionnaire_data
from paginas.evaluacion_madurez.views import render_evaluation_page


def render(state: EvaluationState):
    """
    Punto de entrada para la herramienta de evaluación.
    Carga los datos del cuestionario y llama a la vista principal.
    """
    theme_1.generate_evaluation_tool_css()

    try:
        CUESTIONARIO = load_questionnaire_data()
        if CUESTIONARIO:
            render_evaluation_page(CUESTIONARIO, state)
        else:
            st.error("No se pudo cargar la configuración del cuestionario.")

    except Exception as e:
        st.error(f"Error al cargar la herramienta de evaluación: {e}")
        st.error("Por favor, asegúrate de que el archivo `config/cuestionario.yaml` exista y tenga el formato correcto.")