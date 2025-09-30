# app_state.py

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class EvaluationState:
    """
    Define la estructura de estado para el módulo de Evaluación de Madurez.
    Esto reemplaza a state_keys.py y las variables sueltas.
    """
    current_section: str = 'TRL 1-3' # Asumimos un valor inicial seguro
    eval_view_mode: str = 'cuestionario'
    all_answers: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, str] = field(default_factory=dict)
    last_eval_results: Dict[str, Any] = field(default_factory=dict)
    hitos_sin_evidencia: List[str] = field(default_factory=list)
    pdf_report_data: bytes = None
    modo_puesta_al_dia: bool = False
    
    # Banderas para los callbacks
    run_submission: bool = False
    save_flags: Dict[str, bool] = field(default_factory=dict)

@dataclass
class AppState:
    """
    El objeto de estado central para TODA la aplicación.
    Por ahora, solo contiene el estado de la evaluación.
    """
    evaluacion: EvaluationState = field(default_factory=EvaluationState)
    # Aquí añadiremos en el futuro:
    # variables_economicas: EconomicVariablesState = field(default_factory=EconomicVariablesState)
    # cbs: CBSState = field(default_factory=CBSState)