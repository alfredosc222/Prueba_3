import streamlit as st
from streamlit_option_menu import option_menu
from theme import load_css
from theme_1 import theme_1
from app_state import AppState
from paginas import pagina_bienvenida
from paginas.evaluacion_madurez import pagina_cbs_evaluacion_2
from pathlib import Path

# --- CONFIGURACIÓN INICIAL ---
css_file = Path(__file__).parent / "styles" / "style.css"
load_css(css_file)
st.set_page_config(page_title="Dashboard de Proyecciones", layout="wide", page_icon="")


if 'app_state' not in st.session_state:
    st.session_state.app_state = AppState()


# --- DEFINICIÓN DE PÁGINAS Y SECCIONES ---

# def render_variables_economicas_page():
#     """Renderiza la sección completa de Variables Económicas con su sub-navegación."""
#     theme.render_main_title("Análisis de Variables Económicas", align="center")
    
#     analisis_seleccionado = option_menu(
#         menu_title=None,
#         options=["Inflación México", "Inflación Estados Unidos", "S&P 500", "EMBI", "Beta Desapalancada", "Deuda Largo Plazo", "Bonos 20 años", "Resumen"],
#         icons=['bi-currency-dollar', 'bi-currency-exchange', 'bi-graph-up-arrow', 'bi-globe-americas', 'bi-bar-chart-line', 'bi-cash-stack', 'bi-bank', 'bi-file-earmark-text'],
#         orientation="horizontal",
#         styles={
#             "container": {"padding": "0!important", "background-color": "#fafafa"},
#             "icon": {"color": "#607D8B", "font-size": "20px"}, 
#             "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
#             "nav-link-selected": {"background-color": "#0a3161"},
#         }
#     ) 
    
    # # Enrutador para las sub-páginas de esta sección
    # if analisis_seleccionado == "Inflación México": pagina_inflacion_mex.render()
    # elif analisis_seleccionado == "Inflación Estados Unidos": pagina_inflacion_usa.render() 
    # elif analisis_seleccionado == "S&P 500": pagina_sp500.render()
    # elif analisis_seleccionado == "EMBI": pagina_embi.render()
    # elif analisis_seleccionado == "Beta Desapalancada": pagina_beta.render()
    # elif analisis_seleccionado == "Deuda Largo Plazo": pagina_apalancamiento.render()
    # elif analisis_seleccionado == "Bonos 20 años": pagina_bonos_20.render()
    # elif analisis_seleccionado == "Resumen": pagina_resumen_ve.render()

# def render_cbs_page():
#     """Renderiza la sección completa de CBS, que es manejada por pagina_cbs_central."""
#     # El valor por defecto ahora es el primero en la lista, "Nivel 1-3"
#     segmento_seleccionado = st.session_state.get('segmento_cbs_seleccionado', "Nivel 1-3")
#     segment_map = {
#         "Nivel 1-3": "nivel_1_3",
#         "Nivel 4-6": "nivel_4_6",
#         "Nivel 7-9": "nivel_7_9"
#     }
#     segment_key = segment_map.get(segmento_seleccionado)
#     theme.render_main_title(f"Estructura de Desglose de Costos ({segmento_seleccionado})", align="center")
#     pagina_cbs_central.render_cbs_segment(segment_key)

# "MAPA" O DICCIONARIO ENRUTADOR DE LA APLICACIÓN
PAGES = {
    "Pagina principal": {
        "icon": "bi-house-door",
        "render_func": pagina_bienvenida.render
    },

    "Evaluación de madurez tecnologica TRL/TPL": {
        "icon": "bi-clipboard2-check",
        "render_func": lambda: pagina_cbs_evaluacion_2.render(state=st.session_state.app_state.evaluacion)
    },

    "Variables económicas": {
        "icon": "bi-columns-gap",
        "render_func": lambda: st.info("Página de Flujo de Efectivo en construcción.")
    },

    "CBS": {
        "icon": "bi-collection",
        "render_func": lambda: st.info("Página de Flujo de Efectivo en construcción.")
    },

    "Flujo de efectivo": {
        "icon": "bi-bar-chart-line",
        "render_func": lambda: st.info("Página de Flujo de Efectivo en construcción.")
    }
}

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    theme_1.render_main_title("Menú", align="center")
    
    # El menú se construye dinámicamente a partir de nuestro diccionario PAGES
    page_names = list(PAGES.keys())
    page_icons = [PAGES[page]["icon"] for page in page_names]
    
    pagina_seleccionada = option_menu(
        menu_title=None,
        options=page_names,
        icons=page_icons,
        menu_icon="app-indicator",
        default_index=0,
        styles=theme_1.estilo_menu_principal
    )
    
    # Submenú condicional para CBS (sin cambios)
    if pagina_seleccionada == "CBS":
        #st.markdown('<div class="sidebar-submenu">', unsafe_allow_html=True)
        segmento_cbs = option_menu(
            menu_title="Nivel de LCOE",
            options=["Nivel 1-3", "Nivel 4-6", "Nivel 7-9"],
            icons=["bi-layers-half", "bi-layers-half", "bi-layers-half"],
            menu_icon="list-nested",
            default_index=0,
            styles=theme_1.estilo_submenu
        )
        #st.markdown('</div>', unsafe_allow_html=True)
        st.session_state['segmento_cbs_seleccionado'] = segmento_cbs

# --- ENRUTADOR PRINCIPAL ---
# Esta es la parte más importante. La larga cadena de 'if/elif' desaparece.
render_function = PAGES[pagina_seleccionada]["render_func"]
render_function()