import streamlit as st
from fpdf import FPDF, HTMLMixin
from pathlib import Path
from jinja2 import Template
from collections import defaultdict
from datetime import datetime

# Tus importaciones de otros módulos
from theme_1 import theme_1
from .gaficas import _create_stacked_bar_chart, create_cumulative_stacked_bar_chart
from app_state import EvaluationState
from .data_model import ESTATUS_OPCIONES

# -----------------------------------------------------------------------------
# 1. CLASE PDF PERSONALIZADA
# -----------------------------------------------------------------------------
class PDF(FPDF, HTMLMixin):
    """
    Clase FPDF personalizada que define un encabezado y pie de página
    estándar para todo el reporte, así como un estilo para los títulos de sección.
    """
    def header(self):
        """Define el encabezado que aparecerá en la parte superior de cada página."""
        if self.page_no() > 1:
            self.set_font('DejaVu', '', 9)
            self.cell(0, 10, 'Reporte de maduración tecnológica', 0, 1, 'R')
            self.ln(5)

    def footer(self):
        """Define el pie de página que aparecerá en la parte inferior de cada página."""
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
    def section_title(self, title):
        """Crea un título de sección estandarizado con fondo gris."""
        # 1. Establecemos la fuente y dibujamos el título centrado
        self.set_font('DejaVu', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'C')
        
        # 2. Obtenemos el ancho en mm del texto que acabamos de escribir
        text_width = self.get_string_width(title)
        
        # 3. Calculamos el ancho de nuestra línea (el ancho del texto + 10mm de padding)
        line_width = text_width + 10
        
        # 4. Calculamos la posición 'x' inicial para que la línea quede centrada
        #    (Ancho de la página - Ancho de la línea) / 2
        x_start = (self.w - line_width) / 2
        
        # 5. Configuramos y dibujamos la línea
        self.set_draw_color(theme_1.PALETA_PRIMITIVA["turquesa_profundo"]) # El color de tu tema
        self.set_line_width(0.5)
        self.line(x_start, self.get_y(), x_start + line_width, self.get_y())
        
        # 6. ¡IMPORTANTE! Restauramos el grosor de línea al valor por defecto
        #    para que no afecte a las tablas que se dibujen después.
        self.set_line_width(0.2)
        
        # 7. Añadimos un espacio final
        self.ln(8)

# -----------------------------------------------------------------------------
# 2. FUNCIÓN DE AYUDA PARA GRÁFICOS
# -----------------------------------------------------------------------------
def _add_chart_to_pdf(pdf, chart_figure):
    """
    Convierte una figura de Plotly a imagen y la añade al PDF.
    Esto evita duplicar este bloque de código.
    """
    try:
        img_bytes = chart_figure.to_image(format="png", width=800, height=350, scale=2)
        pdf.image(img_bytes, w=pdf.w - 2 * pdf.l_margin)
        pdf.ln(5)
    except Exception as e:
        pdf.set_font('DejaVu', 'I', 10)
        pdf.multi_cell(0, 6, f"(Error al generar el gráfico: {e})")

# -----------------------------------------------------------------------------
# 3. FUNCIÓN PRINCIPAL DE GENERACIÓN DEL REPORTE
# -----------------------------------------------------------------------------
def generate_robust_pdf_report(CUESTIONARIO, matrix_data, roadmap_data, global_kpis, last_eval_results, state: EvaluationState):
    """
    Genera el reporte ejecutivo completo en formato PDF.

    Args:
        CUESTIONARIO (dict): El diccionario completo del cuestionario.
        matrix_data (dict): Datos pre-calculados para la matriz de madurez.
        roadmap_data (dict): Datos pre-calculados para el desempeño por área.
        global_kpis (dict): KPIs globales del proyecto.
        last_eval_results (dict): Resultados detallados de la última sección evaluada.

    Returns:
        bytes: El contenido del archivo PDF generado.
    """
    pdf = PDF()

    # --- Configuración de Fuentes ---
    try:
        base_dir = Path(__file__).parent
        font_dir = base_dir / "pdf_templates"
        
        # Registramos las dos fuentes que usaremos en todo el documento
        pdf.add_font('DejaVu', '', str(font_dir / 'DejaVuSans.ttf'))
        pdf.add_font('DejaVu', 'B', str(font_dir / 'DejaVuSans-Bold.ttf'))
        
        pdf.set_font('DejaVu', '', 11)
        
    except Exception as e:
        st.error(f"Error crítico al cargar las fuentes DejaVu: {e}")
        return None




    # --- SECCIÓN 0: PORTADA ---
    pdf.add_page()
    pdf.set_y(60)
    
    # Título Principal
    pdf.set_font('DejaVu', 'B', 24)
    pdf.multi_cell(0, 15, 'Informe de estado de desarrollo tecnológico y evaluación de viabilidad', 0, 'C')
    pdf.ln(20) # Espacio grande

    # Subtítulos con información del reporte
    pdf.set_font('DejaVu', '', 18)
    pdf.cell(0, 10, "Nivel de maduración actual del dispositivo undimotriz", 0, 1, 'C')

    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10, f"Fecha de evaluación: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.cell(0, 10, "Versión del reporte: 1.0", 0, 1, 'C')
    



    # --- SECCIÓN 1: KPIs ---
    pdf.add_page()
    pdf.section_title("Resultados generales")
    
    kpis = [
        ("Nivel de TRL", str(global_kpis['trl_global'])),
        ("Progreso general", global_kpis['progreso_general']),
        ("Puntaje total", global_kpis['puntaje_total'])
    ]
    
    col_width = (pdf.w - 2 * pdf.l_margin) / 3
    start_y = pdf.get_y()
    
    for i, (label, value) in enumerate(kpis):
        pdf.set_x(pdf.l_margin + i * col_width)
        pdf.set_font_size(12)
        pdf.set_text_color(78, 107, 115)
        pdf.multi_cell(col_width, 8, label, align='C')
        pdf.set_x(pdf.l_margin + i * col_width)
        pdf.set_font(style='B', size=22)
        pdf.set_text_color(10, 49, 97)
        pdf.multi_cell(col_width, 10, value, align='C')
        pdf.set_y(start_y)

    pdf.set_y(start_y + 25)
    pdf.set_text_color(0, 0, 0)


    # --- SECCIÓN 2: Matriz de Madurez ---
    pdf.section_title("Matriz de maduración tecnológica")

    status_colors = {
        "Completado": theme_1.COLORS["color_1"], 
        "Falta Puntaje": theme_1.COLORS["color_2"],       
        "Falta Hito Crítico": theme_1.COLORS["color_3"],  
        "Pendiente": theme_1.COLORS["color_4"],                           
    }
    
    html_matrix = """
    <table border="1" width="100%">
        <thead>
            <tr>
                <th width="80%"><font size="11">Área de desarrollo</font></th>
                {% for i in range(1, 10) %}<th width="15%"><font size="9">TRL {{i}}</font></th>{% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for eje, trls in matrix_data.items()|sort %}
            <tr>
                <td><font size="9">{{ eje }}</font></td>
                {% for i in range(1, 10) %}
                    {% set trl_key = "TRL " + i|string %}
                    {% set status = trls.get(trl_key, {"status": "-"})["status"] %}
                    <td bgcolor="{{ colors.get(status, '#ffffff') }}">&nbsp;</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    """
    # Usamos Jinja2 implícito en FPDF2 para renderizar la tabla
    template = Template(html_matrix)
    html_final = template.render(matrix_data=matrix_data, colors=status_colors)
    
    # Paso 2: Pasar el HTML puro a FPDF2 (sin el argumento 'context')
    pdf.write_html(html_final, table_line_separators=True)
    pdf.ln(10)




    # --- SECCIÓN 3: Plan de Acción Recomendado ---
    #pdf.add_page()
    pdf.section_title("Plan de acción recomendado para alcanzar el siguiente nivel de TRL")

    # Verificamos si hay resultados y si la evaluación fue aprobada
    if not last_eval_results or last_eval_results.get('aprobado_general', True):
        pdf.set_font('DejaVu', '', 11)
        pdf.multi_cell(0, 6, "¡Felicidades! Todos los requisitos de la última etapa evaluada fueron cumplidos. No hay acciones críticas pendientes para esta fase.")
    else:
        # Recreamos la lógica para encontrar el plan de acción
        seccion_key = last_eval_results['seccion']
        seccion_data = CUESTIONARIO[seccion_key]
        
        # Encontrar el TRL objetivo
        trls_en_seccion = sorted([int(trl.split(" ")[1]) for trl in seccion_data.get("requisitos_por_trl", {}).keys()])
        objetivo_trl_num = next((trl for trl in trls_en_seccion if trl > last_eval_results['trl_alcanzado']), max(trls_en_seccion))
        objetivo_trl_key = f"TRL {objetivo_trl_num}"
        requisitos_siguiente = seccion_data["requisitos_por_trl"][objetivo_trl_key]

        # 1. Hitos Críticos Pendientes
        pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}
        hitos_criticos_pendientes = [
            p['hito'] for p in last_eval_results['preguntas'] 
            if p['id'] in requisitos_siguiente.get("hitos_criticos", []) and 
            pill_a_opcion_key.get(last_eval_results['respuestas_pills'][p['id']]) != "Completado"
        ]
        
        if hitos_criticos_pendientes:
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, f"Avance tecnológico necesario para alcanzar un nivel de {objetivo_trl_key}:", 0, 1, 'L')
            html_content = "<ul>"
            for hito_texto in hitos_criticos_pendientes:
                html_content += f"<li>{hito_texto}</li>"
            html_content += "</ul>"
            pdf.set_font('DejaVu', '', 11)
            pdf.write_html(html_content)
            pdf.ln(5)

        # 2. Ejes con Puntaje Insuficiente
        ejes_deficientes = {
            eje: puntaje_req for eje, puntaje_req in requisitos_siguiente.get("puntajes_minimos", {}).items()
            if last_eval_results['ejes_scores'][eje]['obtenido'] < puntaje_req
        }
        
        if ejes_deficientes:
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, "Otros avances tecnológicos necesarios:", 0, 1, 'L')
            html_content = ""
            for eje, puntaje_req in ejes_deficientes.items():
                puntaje_obt = last_eval_results['ejes_scores'][eje]['obtenido']
                html_content += f"<p><b>{eje}:</b> Se requiere un puntaje de {puntaje_req} y el actual es {puntaje_obt}.</p>"
            pdf.set_font('DejaVu', '', 11)
            pdf.write_html(html_content)
    
    pdf.ln(10)

    # --- SECCIÓN 4: Gráficos ---
    pdf.add_page()
    if last_eval_results:
        pdf.section_title(f"Análisis de sección {last_eval_results['seccion']}")
        section_fig = _create_stacked_bar_chart(last_eval_results)
        _add_chart_to_pdf(pdf, section_fig)

        # Gráfico acumulado (condicional)
        if last_eval_results['seccion'] != list(CUESTIONARIO.keys())[0]:
            pdf.section_title("Progreso acumulado del proyecto")
            all_answers_completo = state.all_answers
            respuestas_pills_flat = {q_id: data.get('pill_label') for q_id, data in all_answers_completo.items()}
            cum_fig = create_cumulative_stacked_bar_chart(CUESTIONARIO, respuestas_pills_flat)
            _add_chart_to_pdf(pdf, cum_fig)




    # --- SECCIÓN 5: Registro de Evidencia ---
    pdf.add_page()
    pdf.section_title("Registro de preguntas marcadas como 'Completada'")

    all_answers = state.all_answers
    pill_a_opcion_key = {data["pill_label"]: key for key, data in ESTATUS_OPCIONES.items()}
    id_a_pregunta = {p['id']: p for sec in CUESTIONARIO.values() for p in sec['preguntas']}
    
    hitos_completados_con_evidencia = []
 
    # Bucle para construir la lista de hitos completados, leyendo la estructura de datos correcta
    for q_id, respuesta_data in all_answers.items():
        # Nos aseguramos de que la respuesta sea un diccionario y que la píldora sea "Completado"
        if isinstance(respuesta_data, dict) and pill_a_opcion_key.get(respuesta_data.get("pill_label")) == "Completado":
            evidencia = {
                "hito": id_a_pregunta.get(q_id, {}).get('hito', 'Pregunta no encontrada'),
                # Leemos la clave correcta para el nombre del archivo
                "archivo_nombre": respuesta_data.get("evidencia_archivo"),
                "tipo_archivo": respuesta_data.get("evidencia_tipo") or "No especificado",
                "justificacion": respuesta_data.get("evidencia_justificacion") or "Sin justificación."
            }
            hitos_completados_con_evidencia.append(evidencia)

    # Bucle para mostrar la evidencia en el PDF
    if not hitos_completados_con_evidencia:
        pdf.set_font('DejaVu', 'I', 11)
        pdf.cell(0, 10, "Aún no se han registrado preguntas marcadas como 'Completada'.")
    else:

        pdf.set_font('DejaVu', '', 10)
        for ev in hitos_completados_con_evidencia:
            # Leemos el nombre del archivo de forma segura
            nombre_archivo = ev.get("archivo_nombre") or "No adjunto"
            

            html_evidencia = f"""
            <p>
            <b>Hito:</b> {ev['hito']}<br><br>
            <b>Evidencia:</b><br>
            <blockquote>
            <b>Archivo:</b> {nombre_archivo}<br>
            <b>Tipo:</b> {ev['tipo_archivo']}<br>
            <b>Justificación:</b> {ev['justificacion']}
            </blockquote>
            </p><hr>
            """
            pdf.write_html(html_evidencia)




    # --- SECCIÓN 6: Anexo de Hitos Pendientes ---
    pdf.add_page()
    pdf.section_title("Anexo: Avances tecnológicos incompletos")

    # Usaremos un diccionario para agrupar los hitos por su eje
    hitos_pendientes_por_eje = defaultdict(list)

    # Bucle para encontrar y agrupar todos los hitos no completados
    for q_id, respuesta_data in all_answers.items():
        if isinstance(respuesta_data, dict):
            status = pill_a_opcion_key.get(respuesta_data.get("pill_label"))
            
            if status and status != "Completado":
                pregunta_completa = id_a_pregunta.get(q_id)
                if pregunta_completa:
                    eje = pregunta_completa.get('eje', 'Sin Área')
                    hito_info = {
                        "hito": pregunta_completa.get('hito', 'Hito no encontrado'),
                        "status": status
                    }
                    hitos_pendientes_por_eje[eje].append(hito_info)

    # Bucle para mostrar los hitos agrupados en el PDF
    if not hitos_pendientes_por_eje:
        pdf.set_font('DejaVu', '', 11)
        pdf.cell(0, 10, "¡Felicidades! No hay hitos pendientes registrados.")
    else:
        # Iteramos sobre cada eje (área) que tiene hitos pendientes
        for eje, hitos in sorted(hitos_pendientes_por_eje.items()):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, f"Área {eje}", 0, 1, 'L')
            html_content = ""
            for hito_info in hitos:
                html_content += f"""
                <p style="margin-bottom: 8px;">
                    &bull; <b>{hito_info['status']}:</b> {hito_info['hito']}<br><br>
                </p>
                """
            
            pdf.set_font('DejaVu', '', 10)
            pdf.write_html(html_content)
            pdf.ln(5)


    return bytes(pdf.output())







