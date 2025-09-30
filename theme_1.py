import streamlit as st
from pathlib import Path

class AppTheme:
    """
    Clase centralizada para gestionar la apariencia de la aplicación.
    Contiene la paleta de colores, estilos para componentes específicos,
    y un generador de CSS global.
    """

    # PALETA_COLORES ={

    # "color_base": "#00686B", # Principal
    # "color_base_2": "#004547", #Titulos

    # # Monocromaticos
    # "color_1": "#2BA7AB",
    # "color_2": "#00686B", # Principal
    # "color_3": "#75E7EB",
    # "color_4": "#BFFDFF",

    # # Triada
    # "colortr_1": "#6B5B00",
    # "colortr_2": "#00686B", # Principal
    # "colortr_3": "#6B0048",
    # "colortr_4": "#40BCC0",

    # # Complementarios
    # "colorcom_1": "#99FCFF",
    # "colorcom_2": "#EBA375",
    # "colorcom_3": "#6B2A00",
    # "colorcom_4": "#00686B", # Principal
    # "colorcom_5": "#0B3738",
    # "colorcom_6": "#AB5C2B",
    # "colorcom_7": "#54CDD1",

    # # Separacion complementaria

    # "colorsecom_1":"#AAFCFF",
    # "colorsecom_2":"#C05B40",
    # "colorsecom_3":"#6B3C00",
    # "colorsecom_4":"#00686B", # Principal
    # "colorsecom_5":"#6B1700",
    # "colorsecom_6":"#40BCC0",
    # "colorsecom_7":"#C08840",

    # # Cuadrado
    # "colorcuad_1": "#40BCC0",
    # "colorcuad_2": "#44006B",
    # "colorcuad_3": "#00686B", # Principal
    # "colorcuad_4": "#576B00",
    # "colorcuad_5": "#6B2A00",

    # # Compuestos
    # "colorcompu_1": "#40BCC0",
    # "colorcompu_2": "#6B2A00",
    # "colorcompu_3": "#00686B", # Principal
    # "colorcompu_4": "#006B32",
    # "colorcompu_5": "#6B4600",

    # "fondo_1": "#FFFFFF",
    # "fondo_2": "#FDFCFB",
    # "fondo_3": "#EFF2F5",

    # }
    
    # # --- 1. PALETA DE COLORES CENTRALIZADA ---
    # COLORS = {

    #     # --- Fondos y Estructura
    #     "fondo_principal": PALETA_COLORES["fondo_2"],
    #     "fondo_barra_lateral": PALETA_COLORES["fondo_3"],
    #     "sub_menu":PALETA_COLORES["fondo_1"],
    #     "sub_sub_menu":PALETA_COLORES["fondo_1"],

    #     # Elementos interactivos hechos con CSS
    #     "fondo_widget": "#FFFFFF",
    #     "borde_principal": "#D5DCE4",
    #     "borde_suave": "#E9ECEF",
    #     "hover_fila": "#F5F2ED",

    #     # Mouse 
    #     "mouse_principal":"#E6F7F7",
    #     "mouse_secundario":"#E6F7F7",
    #     "selec_principal":"#006A6C",
    #     "selec_secundario":"#0A9396",


    #     # Textos y iconos
    #     "texto_principal": PALETA_COLORES["color_base_2"],
    #     "texto_secundario": PALETA_COLORES["color_base"],
    #     "texto_claro": "#FFFFFF",
    #     "iconos_principales":PALETA_COLORES["color_base_2"],
    #     "iconos_secundarios":PALETA_COLORES["color_base"],


    #     # Cuadros de dialogo
    #     #"informacion_transparente": "rgba(0, 106, 108, 0.15)",
    #     "informacion_transparente": "rgba(136, 201, 192, 0.15)",
    #     "informacion_solido": "#006A6C",
    #     #"advertencia_transparente":"rgba(187, 62, 3, 0.15)",
    #     "advertencia_transparente":"rgba(242, 182, 160, 0.15)",
    #     "advertencia_solido":"#BB3E03",
    #     #"exito_transparente": "rgba(10, 147, 150, 0.15)",
    #     "exito_transparente": "rgba(131, 197, 190, 0.25)",
    #     "exito_solido": "#0A9396",

    #     # Preguntas por nivel de importancia
    #     "pregunta_alta": "#00696B" ,
    #     "pregunta_media":"#6B2900",
    #     "pregunta_baja":"#40BEC0",

    #     # Matriz
    #     "color_1":"#0A9396",
    #     "color_2":"#BB3E03",
    #     "color_3":"#AE2012",
    #     "color_4":"#E9ECEF",

    # }


    PONDERACION_STYLES = {
        "Baja":  "font-weight:600;",
        "Media": "font-weight:600;",
        "Alta":  "font-weight:600;", 
    }



    # --- NIVEL 1: PALETA PRIMITIVA (La fuente de la verdad) ---
    # Contiene los colores puros y únicos de tu sistema.
    PALETA_PRIMITIVA = {
        # === Escala Tonal Turquesa ===
        # El corazón de la marca, desde el más oscuro al más claro.
        "turquesa_profundo": "#004547",  # Para texto principal, legible y con carácter.
        "turquesa_principal": "#00686B", # El color base, para acentos y selecciones.
        "turquesa_vibrante": "#2BA7AB",  # Para estados de "éxito" y acentos secundarios.
        "cian_palido": "#BFFDFF",        # Para efectos 'hover' muy sutiles.

        # === Acentos de Estado ===
        # Colores con propósito específico para comunicar mensajes clave.
        "naranja_terracota": "#AB5C2B",   # Para advertencias.
        "rojo_ladrillo": "#AE2012",      # Para errores o hitos críticos.
        "rojo_burgoña": "#9B2226",       # Para "alta importancia", más sofisticado.
        "azul_zafiro": "#0062B3",        # Para distinciones claras en jerarquías.

        # === Escala de Neutros ===
        # Grises de apoyo para dar estructura y legibilidad sin competir.
        "gris_pizarra": "#7B8A9E",      # Para texto secundario e iconos.
        "gris_niebla": "#D5DCE4",       # Para bordes definidos.
        "gris_perla": "#E9ECEF",        # Para fondos de 'pendiente' y bordes suaves.

        # === Fondos Base ===
        # Los lienzos sobre los que se construye la interfaz.
        "blanco_puro": "#FFFFFF",
        "blanco_marfil": "#FDFCFB",
        "gris_frio_claro": "#EFF2F5",
    }

    # --- NIVEL 2: PALETA SEMÁNTICA (El propósito de cada color) ---
    # Ahora, todas las variables apuntan a la paleta primitiva.
    COLORS = {
        # --- Fondos y Estructura ---
        "fondo_principal": PALETA_PRIMITIVA["blanco_marfil"],
        "fondo_barra_lateral": PALETA_PRIMITIVA["gris_frio_claro"],
        "sub_menu": PALETA_PRIMITIVA["blanco_puro"],
        "sub_sub_menu": PALETA_PRIMITIVA["blanco_puro"],
        "fondo_widget": PALETA_PRIMITIVA["blanco_puro"],
        "borde_principal": PALETA_PRIMITIVA["gris_niebla"],
        "borde_suave": PALETA_PRIMITIVA["gris_perla"],
        "hover_fila": "#F5F2ED",
        # Nota: "hover_fila" se eliminó en favor de un sistema más simple.

        # --- Mouse (Interacciones de Menú) ---
        "mouse_principal": PALETA_PRIMITIVA["cian_palido"],
        "mouse_secundario": PALETA_PRIMITIVA["cian_palido"],
        "selec_principal": PALETA_PRIMITIVA["turquesa_principal"],
        "selec_secundario": PALETA_PRIMITIVA["turquesa_vibrante"],

        # --- Textos e Iconos ---
        "texto_principal": PALETA_PRIMITIVA["turquesa_profundo"],
        "texto_secundario": PALETA_PRIMITIVA["gris_pizarra"],
        "texto_claro": PALETA_PRIMITIVA["blanco_puro"],
        "iconos_principales": PALETA_PRIMITIVA["turquesa_profundo"],
        "iconos_secundarios": PALETA_PRIMITIVA["gris_pizarra"],

        # --- Cuadros de Diálogo ---
        "informacion_solido": PALETA_PRIMITIVA["azul_zafiro"],
        "informacion_transparente": "rgba(0, 98, 179, 0.15)",
        "advertencia_solido": PALETA_PRIMITIVA["naranja_terracota"],
        "advertencia_transparente": "rgba(171, 92, 43, 0.15)",
        "exito_solido": PALETA_PRIMITIVA["turquesa_vibrante"],
        "exito_transparente": "rgba(43, 167, 171, 0.15)",

        # --- Preguntas por Nivel de Importancia ---
        "pregunta_alta": PALETA_PRIMITIVA["rojo_burgoña"],
        "pregunta_media": PALETA_PRIMITIVA["azul_zafiro"],
        "pregunta_baja": PALETA_PRIMITIVA["turquesa_principal"],

        # --- Matriz ---
        "color_1": PALETA_PRIMITIVA["turquesa_vibrante"],      # Completado
        "color_2": PALETA_PRIMITIVA["naranja_terracota"],   # Falta Puntaje
        "color_3": PALETA_PRIMITIVA["rojo_ladrillo"],       # Falta Hito Crítico
        "color_4": PALETA_PRIMITIVA["gris_perla"],          # Pendiente
    }


    MATERIAL_ICONS_SVG = {
    "check_circle": """<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="{color}"><path d="M0 0h24v24H0z" fill="none"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>""",
    "warning": """<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="{color}"><path d="M0 0h24v24H0z" fill="none"/><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>""",
    "pending": """<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="{color}"><path d="M0 0h24v24H0z" fill="none"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>""",
    "lock": """<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="{color}"><path d="M0 0h24v24H0z" fill="none"/><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>""",
    "radio_button_unchecked": """<svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 0 24 24" width="20px" fill="{color}"><path d="M0 0h24v24H0z" fill="none"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>"""
    }

    def __init__(self):
        """
        Inicializa la instancia del tema y define los diccionarios
        que dependen de la paleta de colores principal.
        """
        self.PONDERACION_COLORS = {
            "Baja": self.COLORS["pregunta_baja"],
            "Media": self.COLORS["pregunta_media"],
            "Alta": self.COLORS["pregunta_alta"]         
        }

    # --- 2. ESTILOS PARA COMPONENTES ESPECÍFICOS ---
    # Estos diccionarios se usan para los 'styles' de streamlit-option-menu.
    
    @property
    def estilo_menu_principal(self):
        """Estilos para el menú principal en la barra lateral."""
        return {
            "container": {"padding": "0!important", "background-color": self.COLORS['sub_menu']},
            "icon": {"color": self.COLORS['iconos_principales'], "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"5px", "--hover-color": self.COLORS['mouse_principal']},
            "nav-link-selected": {"background-color": self.COLORS['selec_principal']},
        }

    @property
    def estilo_submenu(self):
        """Estilos para los submenús (ej. en la barra lateral o en la página)."""
        return {
            "container": {"padding": "0!important", "background-color": self.COLORS['sub_sub_menu']},
            "icon": {"color": self.COLORS['iconos_secundarios'], "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "center", "margin":"2px", "--hover-color": self.COLORS['mouse_secundario']},
            "nav-link-selected": {"background-color": self.COLORS['selec_secundario']},
            "menu-title": {"color": self.COLORS['texto_secundario'], "font-size": "16px", "font-weight": "600", "text-align": "center"}
        }

    # --- 3. PLANTILLAS Y GENERADOR DE CSS GLOBAL ---
    
    def _get_fuentes_css(self) -> str:
        """Devuelve el CSS para la importación de fuentes."""
        return "@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display.swap');"

    def _get_columna_pegajosa_css(self) -> str:
        """Devuelve el CSS para la columna 'sticky' del cuestionario."""
        return """
            div[data-testid="stHorizontalBlock"] {
                align-items: flex-start;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
                position: -webkit-sticky; /* Para compatibilidad con Safari */
                position: sticky;
                top: 60px; /* Distancia desde la parte superior de la pantalla */
            }
        """

    def _get_tarjetas_feedback_css(self) -> str:
        """Devuelve el CSS para las tarjetas de feedback, usando los colores del tema."""
        return f"""
            .feedback-warning {{ background-color: {self.COLORS['advertencia_transparente']}; border-left: 5px solid {self.COLORS['advertencia_solido']}; padding: 1rem; border-radius: 0.25rem; }}
            .feedback-info {{ background-color: {self.COLORS['informacion_transparente']}; border-left: 5px solid {self.COLORS['informacion_solido']}; padding: 1rem; border-radius: 0.25rem; }}
            .feedback-success {{background-color: {self.COLORS['exito_transparente']}; border-left: 5px solid {self.COLORS['exito_solido']}; padding: 1rem; border-radius: 0.25rem; margin-bottom: 0.5rem;}}
        """
        
    def _get_matriz_madurez_css(self) -> str:
        """Devuelve el CSS para la Matriz de Madurez, usando los colores del tema."""
        return f"""
            .maturity-matrix {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; font-family: 'Poppins', sans-serif; }}
            
            .maturity-matrix th {{ 
                background-color: {self.COLORS['fondo_widget']}; color: {self.COLORS['texto_principal']}; font-size: 0.8rem; padding: 0.75rem; 
                text-align: center; border-radius: 6px; font-weight: 600; border-bottom: 2px solid {self.COLORS['borde_suave']};
            }}
            .maturity-matrix .eje-header {{ 
                text-align: center; vertical-align: middle; font-weight: 600;
            }}

            .maturity-matrix tr {{
                transition: background-color 0.2s ease-in-out;
            }}
            .maturity-matrix tr:hover {{
                background-color: {self.COLORS['hover_fila']}; 
            }}

            .maturity-matrix td {{ 
                border: none; height: 45px; text-align: center; 
                vertical-align: middle; border-radius: 6px; position: relative; 
                padding: 5px 0; border: 2px solid {self.COLORS['borde_suave']}; transition: all 0.2s ease-in-out;
            }}
            .maturity-matrix tr:last-child td {{
                border-bottom: none;
            }}

            .maturity-matrix td:hover {{
                transform: scale(1.05) translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
                z-index: 2; border-color: transparent;
            }}
            .maturity-matrix .eje-label {{ 
                text-align: left; font-weight: 600; color: {self.COLORS['texto_principal']}; 
                background-color: {self.COLORS['fondo_widget']}; width: 30%; padding-left: 1rem;
                border: 2px solid {self.COLORS['borde_suave']}; 
            }}


            .status-completado {{ background-color: {self.COLORS['color_1']};  box-shadow: inset 0 1px 2px rgba(0,0,0,0.1); }}
            .status-falta-puntaje {{ background-color: {self.COLORS['color_2']};  box-shadow: inset 0 1px 2px rgba(0,0,0,0.1); }}
            .status-falta-hito {{ background-color: {self.COLORS['color_3']}; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1); }}
            .status-pendiente {{ background-color: {self.COLORS['color_4']}; }}

            /* Tooltips */
            .maturity-matrix td .tooltip {{
                visibility: hidden; width: 220px; background-color: {self.COLORS['texto_principal']}; color: {self.COLORS['texto_claro']};
                text-align: left; border-radius: 6px; padding: 8px 12px; position: absolute;
                z-index: 1; bottom: 125%; left: 50%; margin-left: -110px;
                opacity: 0; transition: opacity 0.3s; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            .maturity-matrix td:hover .tooltip {{ visibility: visible; opacity: 1; }}
            .tooltip-title {{ font-weight: bold; border-bottom: 1px solid rgba(255, 255, 255, 0.2); padding-bottom: 4px; margin-bottom: 4px; }}
            .tooltip-content {{ font-size: 0.8rem; }}

            /* Leyenda */
            .legend-container {{
                display: flex; flex-wrap: wrap; justify-content: center;
                gap: 1.5rem; padding: 0.5rem;
            }}
            .legend-item {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; color: {self.COLORS['texto_principal']}; }}
            .legend-color-box {{ width: 18px; height: 18px; border-radius: 4px; }}
        """


    @st.cache_resource
    def generate_global_css(_self):
        """
        Combina y renderiza los estilos GENERALES para toda la aplicación.
        """
        # Aquí solo se incluyen los estilos que se usan en todas las páginas.
        css_blocks = [
            _self._get_fuentes_css(),
            # En el futuro, aquí podrías añadir otros estilos globales,
            # como los de la barra lateral, etc.
        ]
        
        full_css = "\n".join(css_blocks)
        st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)

    @st.cache_resource
    def generate_evaluation_tool_css(_self):
        """
        Combina y renderiza los estilos PARTICULARES de la herramienta de evaluación.
        """
        # Aquí se incluyen solo los estilos que necesita esta página específica.
        css_blocks = [
            _self._get_columna_pegajosa_css(),
            _self._get_tarjetas_feedback_css(),
            _self._get_matriz_madurez_css()
        ]
        
        full_css = "\n".join(css_blocks)
        st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)

    
    # --- 4. MÉTODOS DE RENDERIZADO ---


    # Nivel 0: Encabezado principal de la app
    def render_main_title(self, title, align="left"):
        st.markdown(f"""
        <div style="margin-bottom: 0px;">
            <h1 style="color: {self.COLORS['texto_principal']}; font-family: 'Poppins', sans-serif; font-size: 48px; font-weight: 600; margin-bottom: 32px; text-align: {align};">
                {title}
            </h1>
        </div>
        """, unsafe_allow_html=True)

    # Nivel 1: Título principal de página
    def render_title(self, text, align="left"):
        st.markdown(f"""
        <h1 style="color: {self.COLORS['texto_principal']}; font-family: 'Poppins', sans-serif; font-size: 36px; font-weight: 600; margin-bottom: 24px; text-align: {align};">
            {text}
        </h1>
        """, unsafe_allow_html=True)

    
    # Nivel 2: Encabezado de sección principal
    def render_header(self, text, align="left"):
        st.markdown(f"""
        <h2 style="color: {self.COLORS['texto_principal']}; font-family: 'Poppins', sans-serif; font-size: 28px; font-weight: 600; line-height: 1.3; margin-top: 16px; margin-bottom: 16px; text-align: {align};">
            {text}
        </h2>
        """, unsafe_allow_html=True)

    # Nivel 3: Subtítulo dentro de una sección o tarjeta
    def render_subheader(self, text, align="left"):
        st.markdown(f"""
        <h3 style="color: {self.COLORS['texto_principal']}; font-family: 'Poppins', sans-serif; font-size: 20px; font-weight: 600; margin-bottom: 8px; text-align: {align};">
            {text}
        </h3>
        """, unsafe_allow_html=True)

    # Nivel 4: Etiqueta para un formulario o grupo de widgets
    def render_label(self, text, align="left"):
        st.markdown(f"""
        <h4 style="color: {self.COLORS['texto_secundario']}; font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: 500; margin-bottom: 4px; text-align: {align};">
            {text}
        </h4>
        """, unsafe_allow_html=True)

    # Nivel 5: Texto normal
    def render_text(self, text, align="justify"):
        st.markdown(f"""
        <p style="color: {self.COLORS['texto_principal']}; font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: 400; line-height: 1.6; margin-bottom: 16px; text-align: {align};">
            {text}
        </p>
        """, unsafe_allow_html=True)

    # Nivel 6: Texto pequeño para notas o pies de foto
    def render_caption(self, text, align="center"):
        st.markdown(f"""
        <p style="color: {self.COLORS['texto_secundario']}; font-family: 'Poppins', sans-serif; font-size: 14px; font-weight: 400; font-style: italic; line-height: 1.4; margin-bottom: 8px; text-align: {align};">
            {text}
        </p>
        """, unsafe_allow_html=True)

    #REVISAR SI SE NECESITA
    def render_sidebar_subheader(self, text, align="center"):
        st.sidebar.markdown(f"""
        <h3 style="color: {self.COLORS['texto_principal']}; font-size: 18px; font-weight: 600; margin-bottom: 5px; text-align: {align};">{text}</h3>
        """, unsafe_allow_html=True)

    # KPIs
    def render_metric(self, label, value, formato=None):
        formatted_value = str(value)
        if formato == '$':
            try: formatted_value = f"${float(value):,.2f}"
            except (ValueError, TypeError): pass
        elif formato == '%':
            formatted_value = f"{value}%"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <span style="font-size: 16px; color: {self.COLORS['texto_secundario']};">{label}</span>
            <p style="font-size: 28px; font-weight: bold; color: {self.COLORS['texto_principal']}; margin-bottom: 0;">{formatted_value}</p>
        </div>
        """, unsafe_allow_html=True)

    # Renderizar iconos
    def render_icon(self, icon_name: str, color: str = "currentColor"):
        """
        Busca un icono SVG en el diccionario y le da formato con el color deseado.
        
        Args:
            icon_name (str): El nombre de la clave del icono (ej. "check_circle").
            color (str): El color para el icono (ej. "#FFFFFF" o self.COLORS['exito_solido']).
        
        Returns:
            str: El string HTML del SVG listo para ser renderizado.
        """
        icon_svg = self.MATERIAL_ICONS_SVG.get(icon_name, "")
        return icon_svg.format(color=color)

theme_1 = AppTheme()