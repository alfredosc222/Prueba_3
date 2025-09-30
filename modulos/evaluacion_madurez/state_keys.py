# eval_tool/state_keys.py

class StateKeys:
    """
    Esta clase no guarda datos. Solo actúa como un 'llavero'
    para tener todas las claves de st.session_state en un solo lugar
    y evitar errores de tipeo.
    """
    # Claves Principales
    CURRENT_SECTION = 'current_section'
    EVAL_VIEW_MODE = 'eval_view_mode'
    ALL_ANSWERS = 'all_answers'
    SCORES = 'scores'
    LAST_EVAL_RESULTS = 'last_eval_results'
    
    # Claves Temporales o de UI
    HITOS_SIN_EVIDENCIA = 'hitos_sin_evidencia'
    PDF_REPORT_DATA = 'pdf_report_data'
    MODO_PUESTA_AL_DIA = 'modo_puesta_al_dia'