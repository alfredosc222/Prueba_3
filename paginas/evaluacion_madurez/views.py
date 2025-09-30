import streamlit as st
from collections import defaultdict
from theme_1 import theme_1
from app_state import EvaluationState

# Importar datos y lógica de los otros módulos
from modulos.evaluacion_madurez.data_model import ESTATUS_OPCIONES, PONDERACION_MAP, load_instructions_text, load_feedback_templates
from modulos.evaluacion_madurez.logic import guardar_evidencia, handle_submission, continuar_seccion, volver_al_cuestionario, set_view_mode, _calculate_maturity_matrix_data,volver_a_resultados, reiniciar_evaluacion_completa, _calculate_global_kpis,_calculate_roadmap_data
from modulos.evaluacion_madurez.pdf_report import generate_robust_pdf_report
from modulos.evaluacion_madurez.gaficas import _create_stacked_bar_chart, create_cumulative_stacked_bar_chart
TEMPLATES = load_feedback_templates()

# Pagina 1/3 muestra el cuestionario
def _render_questionnaire_view(CUESTIONARIO: dict, state: EvaluationState):
    """
    Dibuja la página del cuestionario con las preguntas de la sección actual,
    agrupadas por eje temático.
    """

    # --- PASO CLAVE 1: PROCESAR LAS BANDERAS AL INICIO ---
    # Procesamos la bandera del cálculo final
    if state.run_submission:
        state.run_submission= False

        # 1. Ejecutamos la lógica y capturamos el mensaje que devuelve
        mensaje_error = handle_submission(CUESTIONARIO, state)
        
        # 2. Si la función devolvió un mensaje de error, lo mostramos
        if mensaje_error:
            st.toast(mensaje_error, icon=":material/error:")
            #st.rerun() # Hacemos rerun para que el usuario se quede en la misma página y corrija
        else:
            #Si no hubo error (mensaje es None), procedemos a la página de resultados
            st.rerun()

    # Procesamos las banderas de guardado de evidencia individuales
    seccion_actual_data = CUESTIONARIO[state.current_section]
    for p in seccion_actual_data["preguntas"]:
        if state.save_flags.get(p['id'], False):
            guardar_evidencia(state, p['id'])
            # No hacemos rerun aquí para que el usuario no pierda el scroll

    # --- FIN DEL PROCESAMIENTO DE BANDERAS ---

    seccion_actual_key = state.current_section
    col_cuestionario, col_instrucciones = st.columns([2, 1])

    # --- Columna Izquierda: Cuestionario ---
    with col_cuestionario:
        # Agrupa las preguntas por su "eje" para mostrarlas en tarjetas separadas
        preguntas_agrupadas = defaultdict(list)
        for p in seccion_actual_data["preguntas"]:
            preguntas_agrupadas[p['eje']].append(p)

        # # Mapa para traducir la etiqueta de la píldora (lo que ve el usuario) a su clave interna
        pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}

        # Itera sobre cada grupo de preguntas para crear una tarjeta por eje
        for eje, preguntas_en_eje in preguntas_agrupadas.items():
            with st.container(border=True):
                theme_1.render_header(eje, align="center")
                st.write("")

                # Itera sobre cada pregunta dentro del eje actual
                for i, pregunta in enumerate(preguntas_en_eje):
                    col_pregunta, _, col_estatus = st.columns([10, 1, 8])

                    with col_pregunta:
                        # Aplica el color y estilo de la ponderación al texto del hito
                        ponderacion = pregunta['ponderacion']
                        color = theme_1.PONDERACION_COLORS.get(ponderacion, "#000000")
                        style = theme_1.PONDERACION_STYLES.get(ponderacion, "font-weight: normal;")
                        st.markdown(
                            f"""
                            <p style="color:{color};
                                    {style}
                                    text-align: justify;
                                    margin: 0;
                                    line-height: 1.5;">
                                {pregunta["hito"]}
                            </p>
                            """,
                            unsafe_allow_html=True
                        )
                    #Cambio en esta seccion
                    with col_estatus:
                        # Muestra las píldoras de selección de estatus
                        opciones_pills = [data["pill_label"] for data in ESTATUS_OPCIONES.values()]
                        st.pills(
                            label=pregunta["id"], 
                            options=opciones_pills, 
                            key=pregunta["id"],
                            label_visibility="collapsed"
                        )

                        selected_pill_label = st.session_state.get(pregunta['id'])
                        selected_key = pill_a_opcion_key.get(selected_pill_label)
                        
                        
                        # Si la píldora está en "Completado", se muestra el expander
                        if selected_key == "Completado":
                            hitos_con_error = state.hitos_sin_evidencia
                            tiene_error = pregunta['id'] in hitos_con_error
                            expander_label = f" Registrar información (Obligatorio)" if tiene_error else "Registrar información"

                            with st.expander(expander_label, expanded=tiene_error):
                                # Widgets para la evidencia
                                st.file_uploader("Archivo", key=f"{pregunta['id']}_file", label_visibility="collapsed")
                                # st.selectbox(
                                #     "Tipo de archivo", 
                                #     options=["Análisis/Simulación", "Diseño/Planos", "Reporte de pruebas en laboratorio", "Reporte de pruebas en entorno relevante","Modelo/Hoja de calculo tecnoeconómico", "Plan de negocio/Documento estratégico", "Cotización/Hoja de especificaciones de proveedor", "Minuta de decisión/Revisión de diseño"], 
                                #     key=f"{pregunta['id']}_file_type",
                                #     placeholder="Selecciona una opción",
                                #     #label_visibility="collapsed",
                                # )

                                placeholder = "Selecciona un tipo de archivo..."
                                opciones_reales = [
                                    "Análisis/Simulación", "Diseño/Planos", "Reporte de pruebas en laboratorio",
                                    "Reporte de pruebas en entorno relevante", "Modelo/Hoja de calculo tecnoeconómico",
                                    "Plan de negocio/Documento estratégico", "Cotización/Hoja de especificaciones de proveedor",
                                    "Minuta de decisión/Revisión de diseño"
                                ]
                                opciones_finales = [placeholder] + opciones_reales
                                
                                st.selectbox(
                                    "Tipo de archivo",
                                    options=opciones_finales,
                                    index=0, # Muestra el placeholder por defecto
                                    key=f"{pregunta['id']}_file_type"
                                )

                                st.text_area("Justificación", key=f"{pregunta['id']}_justification", help="Explica brevemente cómo el archivo adjunto respalda el avance tecnológico requerido en esta pregunta.")

                                # --- LÓGICA DEL BOTÓN DE GUARDADO CONDICIONAL ---
                                # 1. Obtenemos los valores guardados en nuestro estado persistente
                                datos_guardados = state.all_answers.get(pregunta['id'], {})


                                nombre_guardado = datos_guardados.get('evidencia_archivo')
                                archivo_actual = st.session_state.get(f"{pregunta['id']}_file")
                                nombre_actual = None
                                if hasattr(archivo_actual, 'name'):
                                    nombre_actual = archivo_actual.name

                                tipo_guardado = datos_guardados.get('evidencia_tipo')
                                tipo_actual = st.session_state.get(f"{pregunta['id']}_file_type")

                                if tipo_actual == placeholder:
                                    tipo_actual = None

                                just_guardada = datos_guardados.get('evidencia_justificacion')
                                just_actual = st.session_state.get(f"{pregunta['id']}_justification")

                                
                                

                                # 3. Comparamos si hay cambios
                                hay_cambios = (
                                    nombre_actual != nombre_guardado or
                                    tipo_actual != tipo_guardado or
                                    # just_actual != just_guardada
                                    (just_actual or "") != (just_guardada or "")
                                )

                                # 4. Si hay cambios, mostramos el botón de guardado
                                if hay_cambios:
                                    st.button(
                                        "Guardar Evidencia", 
                                        key=f"save_btn_{pregunta['id']}", 
                                        on_click=lambda pid=pregunta['id']: state.save_flags.update({pid: True}),
                                        type="primary"
                                    )
                                
                                else:
                                    # Verificamos que haya algo guardado antes de mostrar el botón
                                    if nombre_guardado or tipo_guardado or just_guardada:
                                        st.button(
                                            "Actualizar Evidencia", 
                                            key=f"update_btn_{pregunta['id']}",
                                            on_click=lambda pid=pregunta['id']: state.save_flags.update({pid: True}),
                                            type="primary"
                                        )
                    
                    if i < len(preguntas_en_eje) - 1:
                        st.markdown("<hr style='border: 0px solid #ECEFF1;'>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------
        # PASO 3: Botón de Cálculo Final
        # -------------------------------------------------------------------------
        st.write("")
        _, col_submit, _ = st.columns(3)
        with col_submit:
            # Este botón solo levanta la "bandera" para el cálculo final
            st.button(
                "Calcular puntaje", 
                on_click=lambda: setattr(state, 'run_submission', True), 
                type="primary", 
                use_container_width=True
            )

    # --- Columna Derecha: Instrucciones, Simbologia y Progreso ---
    with col_instrucciones:

        with st.container(border=True):
            theme_1.render_subheader("Nivel de importancia", align="center")
            
            # Se crean columnas para mostrar la leyenda en formato horizontal.
            legend_cols = st.columns(len(theme_1.PONDERACION_COLORS))
            
            # Se itera sobre los diccionarios para crear cada item de la leyenda en su propia columna.
            for i, (ponderacion, color) in enumerate(theme_1.PONDERACION_COLORS.items()):
                with legend_cols[i]:
                    style = theme_1.PONDERACION_STYLES.get(ponderacion, "")
                    # Se usa un div con flexbox para alinear el cuadro de color y el texto.
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                        <div style="width: 15px; height: 15px; background-color: {color}; border-radius: 3px; margin-right: 8px; border: 1px solid rgba(0,0,0,0.1);"></div>
                        <span style="color: {color}; {style}">{ponderacion}</span>
                    </div>
                    """, unsafe_allow_html=True)
            st.write("")

        with st.container(border=True):
            theme_1.render_subheader("Instrucciones", align="center")
            instructions_text = load_instructions_text()
            st.markdown(instructions_text.get("proposito", "Texto no encontrado."), unsafe_allow_html=True)

            # Boton que tiene por función activar o desactivar la carga de datos obligatoria/opcional
            secciones = list(CUESTIONARIO.keys())
            if seccion_actual_key != secciones[-1]:
                state.modo_puesta_al_dia = st.toggle(
                    "Me encuentro en un nivel de TRL superior",
                    value=state.modo_puesta_al_dia,
                    help="Activa esta opción si estás en una fase **TRL avanzada** a la mostrada en este cuestionario. Es necesario contestar el cuestionario para tener un registro de las fases de TRL previas a las que se encuentra, sin embargo, **no se le pedira adjuntar la evidencia** de que completo los requisitos mínimos previstos."
                )
            else:
                # Si es la última sección, se muestra un mensaje informativo.
                st.markdown(TEMPLATES.get('ultimo_cuestionario', ''), unsafe_allow_html=True)
        
            with st.expander("Ver mas"):
                st.markdown(instructions_text.get("vermas", "Texto no encontrado."), unsafe_allow_html=True)

        with st.container(border=True):
            theme_1.render_subheader("Progreso", align="center")
            render_completion_stats(seccion_actual_data)
            render_progress_bar(CUESTIONARIO, seccion_actual_key)
 


# Pagina 1/3 muestra la barra de progreso
def render_progress_bar(CUESTIONARIO: dict, current_section: str):
    """
    Renderiza una barra de progreso que muestra el avance general del usuario
    a través de las diferentes secciones del cuestionario (TRL 1-3, 4-6, etc.).

    Args:
        CUESTIONARIO (dict): El diccionario completo del cuestionario.
        current_section (str): La clave de la sección actual en la que se encuentra el usuario.
    """
    # Obtener la lista de todas las secciones para determinar el progreso
    sections = list(CUESTIONARIO.keys())
    
    try:
        # Encontrar el índice de la sección actual (0 para la primera, 1 para la segunda, etc.)
        current_index = sections.index(current_section)
        total_sections = len(sections)
        
        # Calcular el progreso como un valor entre 0.0 y 1.0
        # Se suma 1 al índice para que la primera sección muestre progreso y no 0%
        progress = (current_index + 1) / total_sections
        
        # Dibujar la barra de progreso y el texto descriptivo
        st.progress(progress)
        theme_1.render_caption(f"Sección {current_index + 1} de {total_sections}", align="center")

    except (ValueError, IndexError):
        # Manejo de errores en caso de que la sección actual no se encuentre en la lista
        st.progress(0)
        theme_1.render_caption("Iniciando evaluación...", align="center")


# Pagina 1/3 muestra el numero de preguntas totales y faltantes
def render_completion_stats(seccion_data: dict):
    """
    Muestra dos KPIs: el número total de preguntas en la sección actual y
    cuántas de ellas ya han sido respondidas por el usuario.

    Args:
        seccion_data (dict): El diccionario de datos para la sección actual del cuestionario.
    """
    # Contar el número total de preguntas en la sección
    total_preguntas = len(seccion_data["preguntas"])
    
    # Contar cuántas preguntas tienen una respuesta guardada en el estado de la sesión
    respondidas = 0
    for p in seccion_data["preguntas"]:
        if st.session_state.get(p["id"]) is not None:
            respondidas += 1
    
    # Crear dos columnas para mostrar las métricas lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        theme_1.render_metric("Número de preguntas", total_preguntas)
    
    with col2:
        theme_1.render_metric("Preguntas respondidas", respondidas)


# Pagina 2/3 muestra toda la pagina (KPIs, recomendaciones y graficas)
def _render_results_view(CUESTIONARIO: dict, state: EvaluationState):
    """
    Dibuja la página completa de resultados después de que el usuario envía una sección.

    Esta vista se compone de varias secciones:
    1. Una tarjeta de resumen con el TRL alcanzado y el veredicto general.
    2. Un panel de KPIs que muestra el progreso hacia el siguiente TRL.
    3. Una sección de dos columnas con un plan de acción detallado y un análisis gráfico.
    4. Un conjunto de botones de navegación para continuar, corregir o finalizar.
    """

    # Se obtienen los resultados del último cálculo guardados en la sesión.
    resultados = state.last_eval_results
    if not resultados:
        st.error("No se encontraron resultados para mostrar.")
        st.button("Volver al cuestionario", on_click=volver_al_cuestionario, args=(state,))
        return

    
    # Mensajes de exito o fracaso 
    if resultados['aprobado_general']:
        st.toast(f"**Has cumplido los requisitos para avanzar.**", icon=":material/celebration:")
    else:
        siguiente_trl = resultados['trl_alcanzado'] + 1
        st.toast(f"Puntaje insuficiente para alcanzar el TRL {siguiente_trl}.", icon=":material/block:")


    st.subheader(f"Nivel actual de maduracion: TRL {resultados['trl_alcanzado']}")

    # Esta sección calcula cuál es el siguiente TRL objetivo y muestra los KPIs de progreso hacia él.   
    seccion_data = CUESTIONARIO[resultados['seccion']]

    trls_en_seccion = []
    
    requisitos = seccion_data.get("requisitos_por_trl", {})
    for trl_key in requisitos.keys():
        try:
            numero_trl = int(trl_key.split(" ")[1])
            trls_en_seccion.append(numero_trl)
        except (IndexError, ValueError):
            continue

    trls_en_seccion.sort()

    
    objetivo_trl_num = None
    for trl in trls_en_seccion:
        if trl > resultados['trl_alcanzado']:
            objetivo_trl_num = trl
            break
            
    if objetivo_trl_num is None and trls_en_seccion:
        objetivo_trl_num = max(trls_en_seccion)

    if objetivo_trl_num:
        objetivo_trl_key = f"TRL {objetivo_trl_num}"
        header_text = f"Progreso hacia {objetivo_trl_key}" if not resultados['aprobado_general'] else f"Requisitos cumplidos para {objetivo_trl_key}"
        
        with st.container(border=True):
            theme_1.render_subheader(header_text)
            requisitos = seccion_data["requisitos_por_trl"][objetivo_trl_key]
            ejes_objetivo = requisitos["puntajes_minimos"]
            
            kpi_cols = st.columns(len(ejes_objetivo))
            for i, (eje, puntaje_req) in enumerate(ejes_objetivo.items()):
                with kpi_cols[i]:
                    puntaje_obt = resultados['ejes_scores'].get(eje, {}).get('obtenido', 0)
                    theme_1.render_metric(eje, f"{puntaje_obt} / {puntaje_req}")

    st.write("")

    # Se comprueba si el modo "Puesta al Día" estaba activo y si el usuario no aprobó.
    if state.modo_puesta_al_dia and not resultados['aprobado_general']:
        st.markdown(
            TEMPLATES.get('diagnostico_puesta_al_dia', '').format(seccion_actual=resultados['seccion']), 
            unsafe_allow_html=True
        )
        st.write("")

    # Analisis gráfico
    col_feedback, col_grafico = st.columns(2)

    with col_feedback:
        theme_1.render_header("Plan de acción recomendado", align="center")   
        pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}

        resultados = state.last_eval_results

        if resultados.get('aprobado_general'):
            
            # 3. PREGUNTA EXTRA: ¿Hemos llegado al final del cuestionario?
            if resultados.get('siguiente_seccion') == 'finalizado':
                st.markdown(TEMPLATES.get('info_finalizado', ''), unsafe_allow_html=True)

            else:
                # Si NO, mostramos el mensaje de siempre para continuar
                st.markdown(TEMPLATES.get('info_continuar', '').format(siguiente_seccion=resultados.get('siguiente_seccion')), unsafe_allow_html=True)

        # # Si el usuario aprobó la sección, se muestra un mensaje de éxito.
        # if resultados['aprobado_general']:
        #     st.markdown(TEMPLATES.get('info_continuar', '').format(siguiente_seccion=resultados['siguiente_seccion']), unsafe_allow_html=True)

        # Si no aprobó, se genera el plan de acción.
        else:
            requisitos_siguiente = seccion_data["requisitos_por_trl"][objetivo_trl_key]
            
            # --- Bloque 1: Identificar y mostrar Hitos Críticos pendientes ---
            hitos_criticos_req = requisitos_siguiente.get("hitos_criticos", [])
            hitos_criticos_fallidos = []

            # Bucle explícito para encontrar los hitos críticos que no están completados.
            for hito_id in hitos_criticos_req:
                respuesta_key = pill_a_opcion_key[resultados['respuestas_pills'][hito_id]]
                if respuesta_key not in ["Completado"]:

                    # Buscar el texto completo del hito
                    hito_texto = next((p['hito'] for p in resultados['preguntas'] if p['id'] == hito_id), "")
                    hitos_criticos_fallidos.append(hito_texto)

            if hitos_criticos_fallidos:
                st.markdown(TEMPLATES.get('hitos_criticos', 'no').format(objetivo_trl_key=objetivo_trl_key), unsafe_allow_html=True)
                for hito_texto in hitos_criticos_fallidos:
                    st.markdown(TEMPLATES.get('hito_individual', '').format(hito_texto=hito_texto), unsafe_allow_html=True)

                st.write("---")

            # --- Bloque 2: Identificar y mostrar Ejes con puntaje insuficiente ---
            ejes_deficientes = {
                eje: {"obtenido": resultados['ejes_scores'][eje]['obtenido'], "requerido": puntaje_req}
                for eje, puntaje_req in requisitos_siguiente.get("puntajes_minimos", {}).items()
                if resultados['ejes_scores'][eje]['obtenido'] < puntaje_req
            }

            # --- Bloque 2: Identificar y mostrar Ejes con puntaje insuficiente ---
            ejes_deficientes = {}
            # Bucle explícito para encontrar los ejes que no alcanzan el puntaje mínimo.
            for eje, puntaje_req in requisitos_siguiente.get("puntajes_minimos", {}).items():
                if resultados['ejes_scores'][eje]['obtenido'] < puntaje_req:
                    ejes_deficientes[eje] = {
                        "obtenido": resultados['ejes_scores'][eje]['obtenido'],
                        "requerido": puntaje_req
                    }

            # --- Bloque 3: Generar la "Ruta Sugerida" para cada eje deficiente ---
            for i, (eje, data) in enumerate(ejes_deficientes.items()):
                with st.container(border=True):
                    puntos_faltantes = data['requerido'] - data['obtenido']

                    # Puntuacion faltante
                    st.markdown(TEMPLATES.get('tarjeta_deficiencia', '').format(eje=eje, puntos_faltantes=puntos_faltantes, puntos_requeridos=data['requerido']), unsafe_allow_html=True)

                    # Se identifican los hitos pendientes para este eje
                    mejoras = []
                    for p in resultados['preguntas']:
                        if p['eje'] == eje and pill_a_opcion_key[resultados['respuestas_pills'][p['id']]] not in ["Completado"]:
                            mejoras.append(p)

                    # Se calcula la ganancia potencial de cada hito                    
                    tareas_con_ganancia = []
                    for hito in mejoras:
                        respuesta_actual_key = pill_a_opcion_key[resultados['respuestas_pills'][hito['id']]]
                        puntaje_actual = ESTATUS_OPCIONES[respuesta_actual_key]['puntaje'] * PONDERACION_MAP[hito['ponderacion']]
                        puntaje_potencial = ESTATUS_OPCIONES['Completado']['puntaje'] * PONDERACION_MAP[hito['ponderacion']]
                        ganancia = puntaje_potencial - puntaje_actual
                        if ganancia > 0:
                            tareas_con_ganancia.append({"hito": hito, "ganancia": ganancia})
                    
                    tareas_con_ganancia.sort(key=lambda x: x['ganancia'], reverse=True)

                    # Se construye la ruta sugerida           
                    puntos_acumulados = 0
                    ruta_sugerida = []
                    for tarea in tareas_con_ganancia:
                        if puntos_acumulados < puntos_faltantes:
                            ruta_sugerida.append(tarea)
                            puntos_acumulados += tarea['ganancia']
                        else:
                            break
                    
                    # Se muestra la ruta sugerida
                    if ruta_sugerida:
                        lista_html = "".join([
                            TEMPLATES.get('ruta_sugerida_item', '').format(
                                ponderacion=tarea['hito']['ponderacion'], 
                                hito=tarea['hito']['hito'], 
                                ganancia=tarea['ganancia']
                            ) for tarea in ruta_sugerida
                        ])
                        st.markdown(TEMPLATES.get('ruta_sugerida_header', '').format(lista_de_hitos=lista_html), unsafe_allow_html=True)

                
                if i < len(ejes_deficientes) - 1:
                    st.write("---")


    with col_grafico:
        theme_1.render_header("Distribución de puntajes por área", align = "center")
        #st.plotly_chart(_create_stacked_bar_chart(resultados), use_container_width=True)
        
        # Se crean dos pestañas (tabs) para organizar las visualizaciones.
        tab_acumulado, tab_detalle = st.tabs(["Progreso acumulado", f"Sección {resultados['seccion']}"])

        # En la primera pestaña, se muestra el nuevo gráfico acumulado.
        with tab_acumulado:
             # --- INICIA LA CORRECCIÓN ---
            # 1. Obtenemos el diccionario completo y complejo de respuestas.
            all_answers_completo = state.all_answers

            # 2. Creamos una versión "plana" y simple solo con las píldoras.
            respuestas_pills_flat = {
                q_id: data.get('pill_label') for q_id, data in all_answers_completo.items()
            }

            # 3. Pasamos la versión plana a la función cacheada.
            cumulative_fig = create_cumulative_stacked_bar_chart(CUESTIONARIO, respuestas_pills_flat)
            # --- TERMINA LA CORRECCIÓN ---
            st.plotly_chart(cumulative_fig, use_container_width=True)

        # En la segunda pestaña, se muestra el gráfico original de la sección.
        with tab_detalle:
            section_fig = _create_stacked_bar_chart(resultados)
            st.plotly_chart(section_fig, use_container_width=True)

    st.write("")
    
    col_regresar, _, col_ruta, _, col_continuar = st.columns([2, 1, 2, 1, 2])
    with col_regresar:
        st.button("Volver a contestar la sección", on_click=volver_al_cuestionario, args=(state,), use_container_width=True)
    
    with col_ruta:
        if resultados['aprobado_general'] and resultados['siguiente_seccion'] != 'finalizado':
            st.button("Proximos pasos y reporte final", on_click=set_view_mode, args=(state,'roadmap',), use_container_width=True)
        else:
            st.button("Reporte final", on_click=set_view_mode, args=(state,'roadmap',), use_container_width=True, type="primary")
    
    with col_continuar:
        if resultados['aprobado_general'] and resultados['siguiente_seccion'] != 'finalizado':
            st.button(f"Continuar a la evaluación para {resultados['siguiente_seccion']}", on_click=continuar_seccion, args=(state,), use_container_width=True, type="primary")




# Pagina 3/3 muestra la matriz de progreso
def _render_maturity_matrix_view(CUESTIONARIO: dict, state: EvaluationState):
    """
    Dibuja la vista de la Hoja de Ruta Tecnológica, que incluye la Matriz de Madurez,
    los botones de acción y el desglose de requisitos por fase.
    """
    theme_1.render_main_title("Matriz de Madurez Tecnológica", align="center")

    st.markdown(TEMPLATES.get('mensaje_matriz', ''), unsafe_allow_html=True)

    # --- INICIA LA CORRECCIÓN ---
    # 1. Obtenemos el diccionario completo y complejo.
    all_answers_completo = state.all_answers

    # 2. Creamos la versión "plana" para las funciones cacheadas.
    respuestas_pills_flat = {
        q_id: data.get('pill_label') for q_id, data in all_answers_completo.items()
    }

    # 3. Usamos la versión plana para los cálculos.
    matrix_data = _calculate_maturity_matrix_data(CUESTIONARIO, respuestas_pills_flat)
    roadmap_data = _calculate_roadmap_data(CUESTIONARIO, respuestas_pills_flat)
    global_kpis = _calculate_global_kpis(matrix_data, roadmap_data)
    # --- TERMINA LA CORRECCIÓN ---

    status_map = {
        "Completado": ("status-completado", "check_circle", "white", "Completado"),
        "Falta Puntaje": ("status-falta-puntaje", "warning", "white", "Falta Puntaje"),
        "Falta Hito Crítico": ("status-falta-hito", "lock", "white", "Falta Hito Crítico"),
        "Pendiente": ("status-pendiente", "radio_button_unchecked", "#7B8A9E", "Pendiente")
    }

    # Leyenda de colores generada dinámicamente con HTML y CSS
    legend_html = '<div class="legend-container">'
    for status, (css_class, icon_name, color, label) in status_map.items():
        legend_html += f'<div class="legend-item"><div class="legend-color-box {css_class}"></div><span>{label}</span></div>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)
    st.write("---")

    # Tabla HTML
    html = '<table class="maturity-matrix"><thead><tr><th class="eje-header">Área de desarrollo</th>'
    for i in range(1, 10): html += f'<th>TRL {i}</th>'
    html += '</tr></thead><tbody>'

    for eje, trls in sorted(matrix_data.items()):
        html += f'<tr><td class="eje-label">{eje}</td>'
        for trl_num in range(1, 10):
            data = trls.get(f"TRL {trl_num}", {"status": "Pendiente", "tooltip": "Sin requisitos definidos."})
            css_class, icon_name, color, label = status_map.get(data['status'], ("status-pendiente", "radio_button_unchecked", "#6a737d", "Pendiente"))
            
            icon_svg = theme_1.render_icon(icon_name, color=color)
            tooltip_html = f'<div class="tooltip"><div class="tooltip-title">{eje} - TRL {trl_num}</div><div class="tooltip-content">{data["tooltip"]}</div></div>'
            html += f'<td class="{css_class}">{icon_svg}{tooltip_html}</td>'
        html += '</tr>'
        
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

    # --- 3. RENDERIZADO DE TARJETAS DE REQUISITOS ---
    _render_requirements_cards(CUESTIONARIO, state)

    # --- 4. RENDERIZADO DE BOTONES DE ACCIÓN (CON LAYOUT DINÁMICO) ---

    # Se comprueba si el PDF está listo para descargar para decidir el layout
    if state.pdf_report_data:
        # Layout de 4 columnas cuando el PDF está listo
        col1, _, col2, _, col3, _, col4 = st.columns([2, 1, 2, 1, 2, 1, 2])
        
        col1.button("Reiniciar el cuestionario", on_click=reiniciar_evaluacion_completa, args=(CUESTIONARIO, state), use_container_width=True)
        col2.button("Volver a los resultados de la sección", on_click=volver_a_resultados, args=(state,), use_container_width=True)
        
        
        # Botón para regenerar el reporte
        if col3.button("Generar nuevo reporte", use_container_width=True):
            state.pdf_report_data= None
            st.rerun()

        # Botón de descarga
        with col4:
            st.download_button(
                label="Descargar reporte",
                data=state.pdf_report_data,
                file_name="reporte_madurez_trl.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
    else:
        # Layout por defecto de 3 columnas
        col1, _, col2, _, col3 = st.columns([2, 1, 2, 1, 2])

        col1.button("Reiniciar el cuestionario", on_click=reiniciar_evaluacion_completa, args=(CUESTIONARIO, state), use_container_width=True)
        col2.button("Volver a los resultados de la seccion", on_click=volver_a_resultados, args=(state,), use_container_width=True)
          
        with col3:
            if st.button("Generar reporte", use_container_width=True, type="primary"):
                with st.spinner("Generando reporte..."):
                    last_eval_results = state.last_eval_results
                    # Llamamos a nuestra nueva y mejorada función
                    pdf_data = generate_robust_pdf_report(
                        CUESTIONARIO=CUESTIONARIO,
                        matrix_data=matrix_data,
                        roadmap_data=roadmap_data,
                        global_kpis=global_kpis,
                        last_eval_results=last_eval_results,
                        state=state
                    )
                    
                    if pdf_data:
                        state.pdf_report_data= pdf_data
                        st.rerun()


# Pagina 3/3 Requisitos para subir de nivel de TRL
def _render_requirements_cards(CUESTIONARIO: dict, state: EvaluationState):
    """
    Dibuja una sección con tarjetas de desglose de requisitos para cada fase del cuestionario.
    
    Para cada fase (TRL 1-3, etc.), crea una columna y dentro de ella, renderiza
    dos secciones principales:
    1. Hitos Críticos: Agrupados por su TRL específico (1, 2, 3...).
    2. Otros Hitos: El resto de los hitos de la fase.
    """
    st.write("")
    
    card_cols = st.columns(len(CUESTIONARIO))
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}

    # --- Función de Ayuda Interna para Evitar Repetir Código ---
    def get_status_icon(respuesta_data):
        """Devuelve el icono de estatus correcto basado en la respuesta."""

        # 1. "Aplanamos" el dato: extraemos la píldora del diccionario
        respuesta_pill = None
        if isinstance(respuesta_data, dict):
            respuesta_pill = respuesta_data.get('pill_label')
        elif isinstance(respuesta_data, str):
            respuesta_pill = respuesta_data # Para compatibilidad con datos antiguos

        if not respuesta_pill:
            return ":material/radio_button_unchecked:"
        
        respuesta_key = pill_a_opcion_key.get(respuesta_pill)
        if respuesta_key in ["Completado"]:
            return ":material/check_circle:"
        elif respuesta_key in ["En planificación", "En desarrollo"]:
            return ":material/pending:"
        return ":material/radio_button_unchecked:"
    
    # Itera sobre cada fase principal (TRL 1-3, TRL 4-6, etc.) para crear una tarjeta
    for i, (fase_key, fase_data) in enumerate(CUESTIONARIO.items()):
        with card_cols[i]:
            with st.container(border=False):
                theme_1.render_header(f"Requisitos para {fase_key}", align="center")
                
                # 1. Crear un set con los IDs de todos los hitos críticos de esta fase
                all_critical_ids = {hito for req in fase_data.get("requisitos_por_trl", {}).values() for hito in req.get("hitos_criticos", [])}
                st.markdown("")

                # 2. Sección de Hitos Críticos
                with st.container(border=True):
                    theme_1.render_subheader("Avance tecnológico necesario para progresar de nivel de TRL", align="center")
                    
                    requisitos_por_trl = sorted(fase_data.get("requisitos_por_trl", {}).items())

                    if not requisitos_por_trl:
                        st.caption("No hay hitos críticos definidos para esta fase.")
                    else:
                        processed_critical_hitos = set()
                        # Itera sobre cada TRL (1, 2, 3...) para mostrar sus nuevos hitos
                        for trl_key, requisitos in requisitos_por_trl:
                            theme_1.render_subheader(f'{trl_key}', align="left")
                            current_hitos = set(requisitos.get("hitos_criticos", []))
                            # Muestra solo los hitos que son NUEVOS en este TRL
                            new_hitos_ids = current_hitos - processed_critical_hitos

                            if not new_hitos_ids:
                                st.caption("_Heredados de TRLs anteriores_")
                            else:
                                for hito_id in sorted(list(new_hitos_ids)):
                                    hito = next((p for p in fase_data['preguntas'] if p['id'] == hito_id), None)
                                if hito:
                                    status_icon = get_status_icon(state.all_answers.get(hito['id']))
                                    st.markdown(f"{status_icon} **{hito['hito']}**")
                            processed_critical_hitos.update(new_hitos_ids)
                
                # 3. Sección de Otros Hitos
                st.markdown("")
                with st.container(border=True):
                    theme_1.render_subheader("Otros avances tecnológicos necesarios", align="center")
                    
                    otros_hitos = [p for p in fase_data['preguntas'] if p['id'] not in all_critical_ids]
                    if not otros_hitos:
                        st.caption("No hay otros hitos definidos para esta fase.")
                    else:
                        for hito in sorted(otros_hitos, key=lambda x: x['id']):
                            status_icon = get_status_icon(state.all_answers.get(hito['id']))
                            st.markdown(f"{status_icon} _{hito['hito']}_")


# Logica principal para cambiar entre paginas
def render_evaluation_page(CUESTIONARIO: dict, state: EvaluationState):
    """
    Función principal que actúa como enrutador de vistas para la herramienta.
    
    Esta función orquesta toda la página de evaluación:
    1. Inyecta el CSS necesario.
    2. Inicializa las variables en el estado de la sesión si no existen.
    3. Determina y muestra el título correcto según la vista actual.
    4. Llama a la función de renderizado apropiada para mostrar la vista
       (cuestionario, resultados, matriz de madurez, o pantalla final).
    """

    # --- 2. Título principal dinámico ---
    # El título de la página cambia según la vista en la que se encuentre el usuario.
    seccion_actual_key = state.current_section

    if state.eval_view_mode == 'resultados':
        resultados = state.last_eval_results
        title_text = f"Resultados de la evaluación para {resultados['seccion']}"
    # elif seccion_actual_key == 'finalizado':
    #     title_text = "Evaluación Completada"
    else:
        title_text = f"Evaluación de madurez del proyecto: {seccion_actual_key}"

    theme_1.render_main_title(title_text, align="center")

    # --- 3. Enrutador de Vistas ---
    if state.eval_view_mode == 'roadmap':
        _render_maturity_matrix_view(CUESTIONARIO, state)
    elif state.eval_view_mode == 'resultados':
        _render_results_view(CUESTIONARIO, state)
    else:
        _render_questionnaire_view(CUESTIONARIO, state)


