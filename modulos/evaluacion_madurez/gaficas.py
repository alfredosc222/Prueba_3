import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import pandas as pd
from theme_1 import theme_1
# Importar los modelos de datos necesarios
from .data_model import ESTATUS_OPCIONES, PONDERACION_MAP

@st.cache_data
def _create_stacked_bar_chart(resultados):
    """
    Crea un gráfico de barras horizontales apiladas que muestra el desglose del puntaje
    ponderado para cada área de desarrollo ("Eje").

    Cada barra está compuesta por micro-segmentos que representan el puntaje
    de una pregunta individual, permitiendo un análisis detallado de la composición
    del avance.

    Args:
        CUESTIONARIO (dict): El diccionario completo del cuestionario, usado para
                             obtener la estructura de preguntas.
        resultados (dict): El diccionario 'last_eval_results' que contiene las
                           respuestas del usuario y otros datos calculados.

    Returns:
        go.Figure: Un objeto de figura de Plotly listo para ser renderizado.
    """
    # --- 1. PREPARACIÓN DE DATOS ---
    # Se itera una sola vez sobre las preguntas para calcular tanto los datos
    # para el gráfico como los puntajes totales para el ordenamiento.

    plot_data = []
    eje_scores = defaultdict(lambda: {"obtenido": 0, "maximo": 0})
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}

    # Iterar sobre las preguntas de la sección actual evaluada.
    for p in resultados['preguntas']:
        eje = p['eje']
        respuesta_pill = resultados['respuestas_pills'][p['id']]
        respuesta_key = pill_a_opcion_key[respuesta_pill]
        
        # Calcular el puntaje obtenido y máximo para esta pregunta específica.
        puntaje_obtenido = ESTATUS_OPCIONES[respuesta_key]['puntaje'] * PONDERACION_MAP[p['ponderacion']]
        puntaje_maximo = ESTATUS_OPCIONES['Completado']['puntaje'] * PONDERACION_MAP[p['ponderacion']]
        
        # Añadir los datos del micro-segmento a la lista para el gráfico.
        plot_data.append({
            "Eje": eje,
            "ID": p['id'],
            "Hito": p['hito'],
            "Ponderacion": p['ponderacion'],
            "Puntaje": puntaje_obtenido
        })

        # Acumular los puntajes para calcular el rendimiento total de cada eje.
        eje_scores[eje]['obtenido'] += puntaje_obtenido
        eje_scores[eje]['maximo'] += puntaje_maximo

    # Si no hay datos, devolver una figura vacía para evitar errores.
    if not plot_data: 
        return go.Figure()

    df_plot = pd.DataFrame(plot_data)

    # --- 2. ORDENAMIENTO DE BARRAS ---
    # Se ordenan los ejes alfabéticamente (A, B, C, D...).
    sorted_ejes = sorted(df_plot['Eje'].unique())
    
    # Se aplica el ordenamiento al DataFrame.
    df_plot['Eje'] = pd.Categorical(df_plot['Eje'], categories=sorted_ejes, ordered=True)
    df_plot = df_plot.sort_values(['Eje', 'ID'])

    # --- 3. CREACIÓN DEL GRÁFICO ---
    # Se utiliza plotly.express para una construcción más sencilla del gráfico de barras.
    fig = px.bar(
        df_plot,
        y='Eje',
        x='Puntaje',
        color='Ponderacion',
        color_discrete_map=theme_1.PONDERACION_COLORS,
        text='ID',
        orientation='h',
    )

    # --- 4. ESTILIZADO Y FORMATO ---
    # Se añaden detalles para mejorar la legibilidad y el diseño.
    fig.update_traces(
        marker_line_width=1.5, marker_line_color='white', # Borde para separar micro-segmentos
        textposition='inside',
        insidetextanchor='middle',
        hovertemplate=(
            "<b>Pregunta:</b> %{text}<br><br>"
            "<b>Puntos obtenidos:</b> %{x}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        barmode='stack',
        height=450,
        xaxis_title="Puntos [1]",
        yaxis_title=None,
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.00, xanchor="right", x=0.9),
        margin=dict(l=210, r=20, t=50, b=50) # Margen izquierdo amplio para las etiquetas de los ejes
    )
    
    return fig

@st.cache_data
def create_cumulative_stacked_bar_chart(CUESTIONARIO: dict, all_answers: dict):
    """
    Crea un gráfico de barras acumulado con el progreso de TODAS las respuestas
    guardadas en la sesión.
    """
    plot_data = []
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}
    
    # 1. Crear un mapa de todas las preguntas para una búsqueda eficiente
    question_map = {p['id']: p for sec in CUESTIONARIO.values() for p in sec['preguntas']}

    # 2. Iterar sobre TODAS las respuestas guardadas en la sesión
    for q_id, respuesta_pill in all_answers.items():
        pregunta = question_map.get(q_id)
        if pregunta:
            eje = pregunta['eje']
            respuesta_key = pill_a_opcion_key[respuesta_pill]
            
            puntaje_obtenido = ESTATUS_OPCIONES[respuesta_key]['puntaje'] * PONDERACION_MAP[pregunta['ponderacion']]
            
            plot_data.append({
                "Eje": eje, "ID": q_id, "Hito": pregunta['hito'],
                "Ponderacion": pregunta['ponderacion'], "Puntaje": puntaje_obtenido
            })

    if not plot_data:
        return go.Figure()

    df_plot = pd.DataFrame(plot_data)

    # 3. Ordenar los ejes alfabéticamente
    sorted_ejes = sorted(df_plot['Eje'].unique())
    df_plot['Eje'] = pd.Categorical(df_plot['Eje'], categories=sorted_ejes, ordered=True)
    df_plot = df_plot.sort_values(['Eje', 'ID'])

    # 4. Crear el gráfico (la lógica es idéntica a la del otro gráfico)
    fig = px.bar(
        df_plot, y='Eje', x='Puntaje', color='Ponderacion',
        color_discrete_map=theme_1.PONDERACION_COLORS, text='ID', orientation='h',
    )
    fig.update_traces(
        marker_line_width=1.5, marker_line_color='white', textposition='inside',
        insidetextanchor='middle',
        hovertemplate=(
            "<b>Pregunta:</b> %{text}<br><br>"
            "<b>Puntos obtenidos:</b> %{x}<extra></extra>"
        )
    )
    fig.update_layout(
        barmode='stack', height=450, xaxis_title="Puntos acumulados [1]",
        yaxis_title=None, legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.00, xanchor="right", x=0.9),
        margin=dict(l=210, r=20, t=50, b=50)
    )
    
    return fig

