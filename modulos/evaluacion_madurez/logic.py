import streamlit as st
from collections import defaultdict
from .data_model import ESTATUS_OPCIONES, PONDERACION_MAP
from app_state import EvaluationState


# --- INICIA LA MEJORA: NUEVA FUNCIÓN DE GUARDADO GRANULAR ---
def guardar_evidencia(state: EvaluationState, question_id: str):
    """
    Guarda los datos de evidencia para una pregunta específica desde los widgets
    de la UI hacia nuestro estado persistente 'ALL_ANSWERS'.
    """
    
    # 1. Obtenemos el diccionario de respuestas del estado
    answers = state.all_answers
    
    # 2. Nos aseguramos de que exista una entrada para esta pregunta
    if question_id not in answers:
        answers[question_id] = {}

    pill_label = st.session_state.get(question_id)

    # --- INICIA LA CORRECCIÓN ---
    # 1. Obtenemos el objeto temporal del archivo
    archivo_obj = st.session_state.get(f"{question_id}_file")
    # 2. Extraemos SOLO el nombre del archivo (que es un string)
    nombre_del_archivo = None
    if hasattr(archivo_obj, 'name'):
        nombre_del_archivo = archivo_obj.name
    # --- TERMINA LA CORRECCIÓN ---

    # 3. Leemos los valores actuales de los widgets de evidencia
    #archivo = st.session_state.get(f"{question_id}_file")
    tipo_archivo = st.session_state.get(f"{question_id}_file_type")
    justificacion = st.session_state.get(f"{question_id}_justification")

    # 4. Actualizamos el estado persistente con los nuevos valores
    answers[question_id]['pill_label'] = pill_label
    answers[question_id]['evidencia_archivo'] = nombre_del_archivo
    answers[question_id]['evidencia_tipo'] = tipo_archivo
    answers[question_id]['evidencia_justificacion'] = justificacion
    
    state.all_answers = answers

    state.save_flags[question_id] = False
    st.toast(f"La evidencia para la pregunta **{question_id}** ha sido guardada.", icon=":material/file_save:")
# --- TERMINA LA MEJORA ---

def handle_submission(CUESTIONARIO: dict, state: EvaluationState):
    """
    Función principal que se ejecuta al presionar 'Calcular Puntaje'.
    1. Valida que todas las preguntas estén respondidas.
    2. Recopila las respuestas y las guarda en el estado global.
    3. Calcula los puntajes por eje.
    4. Determina el TRL alcanzado basado en puntajes y hitos críticos.
    5. Guarda todos los resultados en 'last_eval_results' y cambia a la vista de resultados.
    """

    seccion_actual_key = state.current_section
    preguntas = CUESTIONARIO[seccion_actual_key]["preguntas"]
    
    # --- INICIA EL CAMBIO: Validación de Evidencia y Justificación ---
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}
    
    
    secciones = list(CUESTIONARIO.keys())
    es_obligatorio = not state.modo_puesta_al_dia or seccion_actual_key == secciones[-1]

    if es_obligatorio:
        hitos_sin_evidencia = []
        for p in preguntas:
            respuesta_pill = st.session_state.get(p["id"])
            if pill_a_opcion_key.get(respuesta_pill) == "Completado":
                # Comprueba si falta el archivo O la justificación
                falta_archivo = st.session_state.get(f"{p['id']}_file") is None
                falta_justificacion = not st.session_state.get(f"{p['id']}_justification", "").strip()

                # --- INICIA LA CORRECCIÓN ---
                # 1. Leemos el valor del selectbox
                tipo_archivo_seleccionado = st.session_state.get(f"{p['id']}_file_type")
                
                # 2. Comprobamos si es el placeholder o si está vacío
                falta_tipo_archivo = (
                    tipo_archivo_seleccionado is None or 
                    tipo_archivo_seleccionado == "Selecciona un tipo de archivo..."
                )
                # --- TERMINA LA CORRECCIÓN ---

                if falta_archivo or falta_justificacion or falta_tipo_archivo:
                    hitos_sin_evidencia.append(p['id'])
        
        if hitos_sin_evidencia:
            state.hitos_sin_evidencia = hitos_sin_evidencia
            return f"Falta adjuntar información para {len(hitos_sin_evidencia)} pregunta(s) marcadas como **Completado**."
    
    
    state.hitos_sin_evidencia = []

    # 1. Validación de respuestas
    preguntas_sin_responder = [p for p in preguntas if st.session_state.get(p["id"]) is None]
    if preguntas_sin_responder:
        return f"Por favor, responde las {len(preguntas_sin_responder)} pregunta(s) faltante(s)."
    
    
    # Guardamos o actualizamos solo la selección de la píldora
    for p in preguntas:
        q_id = p['id']
        pill_label = st.session_state.get(q_id)
        
        # Si no existe una entrada para esta pregunta en ALL_ANSWERS, la creamos
        if q_id not in state.all_answers:
            state.all_answers[q_id] = {}
        
        # Actualizamos solo la píldora
        state.all_answers[q_id]['pill_label'] = pill_label


    

    respuestas_pills_actuales = {p['id']: st.session_state.get(p['id']) for p in preguntas}
    

    # 3. Cálculo de puntajes por eje para la sección actual
    ejes_scores = defaultdict(lambda: {"obtenido": 0, "maximo": 0})
    for p in preguntas:
        eje = p['eje']
        # Usamos el diccionario local que acabamos de crear
        respuesta_key = pill_a_opcion_key.get(respuestas_pills_actuales.get(p['id']))
        if respuesta_key:
            puntaje = ESTATUS_OPCIONES[respuesta_key]['puntaje'] * PONDERACION_MAP[p['ponderacion']]
            ejes_scores[eje]['obtenido'] += puntaje
            ejes_scores[eje]['maximo'] += ESTATUS_OPCIONES['Completado']['puntaje'] * PONDERACION_MAP[p['ponderacion']]
    

    
    # 4. Determinación del TRL alcanzado
    secciones = list(CUESTIONARIO.keys())
    baseline_trl = CUESTIONARIO[seccion_actual_key].get('baseline_trl', 0)
    
    trl_alcanzado = baseline_trl
    trls_en_seccion = sorted([int(trl.split(" ")[1]) for trl in CUESTIONARIO[seccion_actual_key]["requisitos_por_trl"].keys()], reverse=True)

    for trl_num in trls_en_seccion:
        trl_key = f"TRL {trl_num}"
        requisitos = CUESTIONARIO[seccion_actual_key]["requisitos_por_trl"][trl_key]
        
        criticos_ok = all(pill_a_opcion_key.get(respuestas_pills_actuales.get(hito_id)) == "Completado" for hito_id in requisitos["hitos_criticos"])
        puntajes_ok = all(ejes_scores[eje]['obtenido'] >= puntaje_minimo for eje, puntaje_minimo in requisitos["puntajes_minimos"].items())

        if criticos_ok and puntajes_ok:
            trl_alcanzado = trl_num
            break
            
    aprobado_general = (trl_alcanzado == max(trls_en_seccion)) if trls_en_seccion else True

    # 5. Guardado de resultados en la sesión
    state.last_eval_results = {
        "seccion": seccion_actual_key,
        "aprobado_general": aprobado_general,
        "trl_alcanzado": trl_alcanzado,
        "ejes_scores": ejes_scores,
        "siguiente_seccion": CUESTIONARIO[seccion_actual_key]["siguiente_seccion"],
        "preguntas": preguntas,
        "respuestas_pills": respuestas_pills_actuales
    }
    state.eval_view_mode= 'resultados'


def continuar_seccion(state: EvaluationState):
    """Avanza a la siguiente sección del cuestionario."""

    resultados = state.last_eval_results
    if resultados and resultados["aprobado_general"]:
        seccion_actual_key = resultados['seccion']
        puntaje_obtenido_total = sum(data['obtenido'] for data in resultados['ejes_scores'].values())
        puntaje_maximo_total = sum(data['maximo'] for data in resultados['ejes_scores'].values())
        porcentaje = (puntaje_obtenido_total / puntaje_maximo_total) * 100 if puntaje_maximo_total > 0 else 0
        state.scores[seccion_actual_key] = f"{porcentaje:.1f}%"
        state.current_section = resultados['siguiente_seccion']
        state.eval_view_mode = 'cuestionario'


def volver_al_cuestionario(state: EvaluationState):
    """Regresa a la vista del cuestionario desde la vista de resultados."""

    state.eval_view_mode = 'cuestionario'


def set_view_mode(state: EvaluationState, mode: str):
    """Establece la vista actual de la página (cuestionario, resultados, roadmap)."""

    state.eval_view_mode = mode

def volver_a_resultados(state: EvaluationState):
    """Regresa a la vista de resultados desde la hoja de ruta."""

    state.eval_view_mode= 'resultados'


def reiniciar_evaluacion_completa(CUESTIONARIO, state: EvaluationState):
    """Resetea todo el estado de la evaluación para empezar de cero."""

    state.current_section = list(CUESTIONARIO.keys())[0]
    state.scores = {}
    state.all_answers = {}
    state.eval_view_mode = 'cuestionario'
    state.last_eval_results = {} # <- Cambio
    state.pdf_report_data = None # <- Cambio


@st.cache_data
def _calculate_max_scores_per_section(CUESTIONARIO):
    """
    Calcula el puntaje máximo posible para cada eje en cada sección del cuestionario.
    Devuelve un diccionario anidado: {seccion: {eje: puntaje_max}}
    """
    max_scores = defaultdict(lambda: defaultdict(int))
    for seccion_key, seccion_data in CUESTIONARIO.items():
        if "preguntas" in seccion_data:
            for pregunta in seccion_data["preguntas"]:
                eje = pregunta['eje']
                puntaje_maximo = ESTATUS_OPCIONES['Completado']['puntaje'] * PONDERACION_MAP[pregunta['ponderacion']]
                max_scores[seccion_key][eje] += puntaje_maximo
    return {k: dict(v) for k, v in max_scores.items()} # Convertir a dict normal


@st.cache_data
def _calculate_maturity_matrix_data(CUESTIONARIO, all_answers: dict):
    """
    Analiza todas las respuestas y determina el estatus para cada Eje vs TRL.
    El resultado se guarda en caché para mejorar el rendimiento.
    """
    max_scores_per_section = _calculate_max_scores_per_section(CUESTIONARIO)
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}
    #id_a_pregunta = {p['id']: p for sec in CUESTIONARIO.values() if "preguntas" in sec for p in sec['preguntas']}
    
    ejes_scores = defaultdict(int)
    for q_id, respuesta_pill in all_answers.items():
        pregunta_data = next((p for sec in CUESTIONARIO.values() for p in sec['preguntas'] if p['id'] == q_id), None)
        if pregunta_data and respuesta_pill:
            respuesta_key = pill_a_opcion_key[respuesta_pill]
            if respuesta_key:
                puntaje = ESTATUS_OPCIONES[respuesta_key]['puntaje'] * PONDERACION_MAP[pregunta_data['ponderacion']]
                ejes_scores[pregunta_data['eje']] += puntaje
                
    matrix_status = defaultdict(dict)
    all_ejes = sorted(list(set(p['eje'] for sec in CUESTIONARIO.values() if "preguntas" in sec for p in sec['preguntas'])))
    secciones = list(CUESTIONARIO.keys())

    for eje in all_ejes:
        for trl_num in range(1, 10):
            trl_key = f"TRL {trl_num}"

            seccion_actual_key = None
            reqs = None
            for key, data in CUESTIONARIO.items():
                if trl_key in data.get("requisitos_por_trl", {}):
                    seccion_actual_key = key
                    reqs = data["requisitos_por_trl"][trl_key]
                    break

            if not reqs:
                matrix_status[eje][trl_key] = {"status": "Pendiente", "tooltip": "Sin requisitos definidos"}
                continue

            # --- LÓGICA DE PUNTAJE ACUMULATIVO ---
            
            # 3. Calcula la base de puntos requerida sumando los máximos de las secciones ANTERIORES.
            baseline_score_requerido = 0
            seccion_index = secciones.index(seccion_actual_key)
            for sec_anterior in secciones[:seccion_index]:
                baseline_score_requerido += max_scores_per_section.get(sec_anterior, {}).get(eje, 0)
            
            # 4. Suma el requisito MÍNIMO de la etapa actual a esa base.
            puntaje_minimo_etapa = reqs['puntajes_minimos'].get(eje, 0)
            puntaje_total_requerido = baseline_score_requerido + puntaje_minimo_etapa

            # 5. Compara el puntaje TOTAL obtenido por el usuario con el puntaje TOTAL requerido.
            puntaje_obt_total = ejes_scores.get(eje, 0)
            puntajes_ok = puntaje_obt_total >= puntaje_total_requerido
            
            # La lógica para verificar los hitos críticos no cambia.
            hitos_criticos_ok = all(
                pill_a_opcion_key.get(all_answers.get(h_id)) == "Completado" 
                for h_id in reqs.get("hitos_criticos", [])
            )
            
            # Determina el estado final de la celda.
            status = "Pendiente"
            if puntajes_ok and hitos_criticos_ok:
                status = "Completado"
            elif not hitos_criticos_ok:
                status = "Falta Hito Crítico"
            elif not puntajes_ok:
                status = "Falta Puntaje"

            tooltip = f"Puntaje Obtenido: {puntaje_obt_total} / Requerido Acumulado: {puntaje_total_requerido}"
            matrix_status[eje][trl_key] = {"status": status, "tooltip": tooltip}
            
    return {k: dict(v) for k, v in matrix_status.items()}

@st.cache_data
def _calculate_roadmap_data(CUESTIONARIO, all_answers: dict):
    """
    Analiza TODAS LAS RESPUESTAS GUARDADAS y calcula el progreso global por eje y fase.
    El resultado se guarda en caché.
    """

    roadmap_data = {}
    all_ejes = sorted(list(set(p['eje'] for sec in CUESTIONARIO.values() for p in sec['preguntas'])))

    for eje in all_ejes:
        roadmap_data[eje] = {
            "total_obtenido": 0, "total_maximo": 0,
            "fases": {'TRL 1-3': {"obtenido": 0, "maximo": 0}, 'TRL 4-6': {"obtenido": 0, "maximo": 0}, 'TRL 7-9': {"obtenido": 0, "maximo": 0}}
        }
        
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}

    for seccion_key, seccion_data in CUESTIONARIO.items():
        for pregunta in seccion_data['preguntas']:
            eje = pregunta['eje']
            puntaje_maximo = ESTATUS_OPCIONES['Completado']['puntaje'] * PONDERACION_MAP[pregunta['ponderacion']]
            roadmap_data[eje]['fases'][seccion_key]['maximo'] += puntaje_maximo
            
            respuesta_pill = all_answers.get(pregunta["id"])
            if respuesta_pill:
                respuesta_key = pill_a_opcion_key.get(respuesta_pill)
                if respuesta_key:
                    puntaje_obtenido = ESTATUS_OPCIONES[respuesta_key]['puntaje'] * PONDERACION_MAP[pregunta['ponderacion']]
                    roadmap_data[eje]['fases'][seccion_key]['obtenido'] += puntaje_obtenido
    
    for eje, data in roadmap_data.items():
        data['total_obtenido'] = sum(fase['obtenido'] for fase in data['fases'].values())
        data['total_maximo'] = sum(fase['maximo'] for fase in data['fases'].values())
            
    return roadmap_data


@st.cache_data
def _calculate_global_kpis(matrix_data, roadmap_data):
    """
    Calcula los KPIs globales del proyecto a partir de los datos pre-calculados.
    El resultado se guarda en caché.
    """
    
    trl_global = 0
    for trl_num in range(1, 10):
        trl_key = f"TRL {trl_num}"
        if all(eje.get(trl_key, {}).get("status") == "Completado" for eje in matrix_data.values()):
            trl_global = trl_num
        else:
            break
            
    # Progreso General
    total_obtenido = sum(data['total_obtenido'] for data in roadmap_data.values())
    total_maximo = sum(data['total_maximo'] for data in roadmap_data.values())
    progreso_general = (total_obtenido / total_maximo) * 100 if total_maximo > 0 else 0
    
    return {
        "trl_global": trl_global,
        "puntaje_total": f"{total_obtenido} / {total_maximo}",
        "progreso_general": f"{progreso_general:.1f}%"
    }

