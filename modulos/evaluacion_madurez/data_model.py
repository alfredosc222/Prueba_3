import streamlit as st
import yaml
from pathlib import Path
import re

ESTATUS_OPCIONES = {
    "No iniciado":       {"puntaje": 0, "pill_label": ":material/radio_button_unchecked: No iniciado", "descripcion": "La tarea aún no ha sido abordada."},
    "En planificación":  {"puntaje": 1, "pill_label": ":material/hourglass_empty: En planificación", "descripcion": "Se han definido la metodología y los recursos."},
    "En desarrollo":     {"puntaje": 2, "pill_label": ":material/autorenew: En desarrollo", "descripcion": "La tarea está en ejecución activa."},
    "Completado":        {"puntaje": 3, "pill_label": ":material/check_circle: Completado", "descripcion": "Resultados documentados y verificados."},
}

PONDERACION_MAP = {"Baja": 1, "Media": 2, "Alta": 3}

@st.cache_resource
def load_questionnaire_data():
    config_path = Path(__file__).parent.parent.parent / "config/cuestionario.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
    

@st.cache_data
def load_instructions_text():
    """
    Lee el archivo de instrucciones y lo divide en un diccionario
    basado en los identificadores '### ID:'.
    """
    instructions_path = Path(__file__).parent.parent.parent / "config/instrucciones.md"
    texts = {}
    try:
        with open(instructions_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Divide el contenido por el identificador, capturando el ID
        sections = re.split(r'### ID:\s*(\w+)', content)
        
        # El resultado es una lista [texto_vacio, id1, contenido1, id2, contenido2, ...]
        # Iteramos de dos en dos para emparejar ID con Contenido
        for i in range(1, len(sections), 2):
            key = sections[i].strip()
            value = sections[i+1].strip()
            texts[key] = value
            
    except FileNotFoundError:
        return {"error": "No se encontró `config/instrucciones.md`."}
    return texts




@st.cache_resource
def load_feedback_templates():
    """
    Lee el archivo de plantillas de feedback y lo divide en un diccionario
    basado en los identificadores '### ID:'.
    """
    templates_path = Path(__file__).parent.parent.parent / "config/feedback_templates.md"
    templates = {}
    try:
        with open(templates_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Divide el contenido por el identificador '### ID: nombre_del_bloque'
        sections = re.split(r'### ID:\s*(\w+)', content)
        
        # El resultado es una lista como: ['', 'id1', 'contenido1', 'id2', 'contenido2', ...]
        # Iteramos de dos en dos para emparejar cada ID con su contenido.
        for i in range(1, len(sections), 2):
            key = sections[i].strip()
            value = sections[i+1].strip()
            templates[key] = value
            
    except FileNotFoundError:
        return {"error": f"No se encontró el archivo de plantillas en `{templates_path}`."}
    return templates


















