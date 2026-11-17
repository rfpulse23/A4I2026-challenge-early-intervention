"""Caregiver Communication Subagent for Plain-Language Bilingual Action Notes."""

from google.adk.agents import LlmAgent
from agent.config import config


def format_caregiver_action_note(
    family_name: str,
    child_name: str,
    origin_clinic: str,
    intake_coordinator: str,
    eval_center: str,
    therapy_vendor: str,
    total_expected_days: int,
    primary_language: str = "Spanish",
) -> dict:
    """Formats a structured, empathetic action plan for caregivers in English and Spanish."""
    english_note = f"""
Dear {family_name} Family,

We have arranged the developmental support pathway for {child_name} through Mississippi First Milestones (IDEA Part C).

Your Next Steps:
1. Intake Coordinator: {intake_coordinator} has received the initial screening packet from {origin_clinic} and will contact you within 4 business days.
2. Developmental Evaluation: A comprehensive evaluation is scheduled at {eval_center}. Spanish-speaking specialists are confirmed, and Medicaid covers 100% of this evaluation at no cost to you.
3. Ongoing Support & Therapy: Following the evaluation, {therapy_vendor} will partner with your family to create {child_name}'s Individualized Family Service Plan (IFSP).

Estimated Timeline: Complete evaluation and service initiation within {total_expected_days} calendar days (well within the federal 45-day protection).
"""

    spanish_note = f"""
Estimada familia {family_name},

Hemos coordinado el plan de apoyo para el desarrollo de {child_name} a través de Mississippi First Milestones (IDEA Parte C).

Sus Próximos Pasos:
1. Coordinación de Ingreso: {intake_coordinator} ha recibido la referencia médica de {origin_clinic} y se comunicará con ustedes dentro de los próximos 4 días hábiles.
2. Evaluación del Desarrollo: Se programará una evaluación completa en {eval_center}. Contamos con especialistas hispanohablantes confirmados, y Medicaid cubre el 100% del servicio sin ningún costo para su familia.
3. Inicio de Terapias: Tras la evaluación, {therapy_vendor} colaborará con ustedes para elaborar el Plan Individualizado de Servicios Familiares (IFSP).

Tiempo Estimado: Todo el proceso se completará en aproximadamente {total_expected_days} días calendario, cumpliendo con la garantía federal de 45 días.
"""

    return {
        "child_name": child_name,
        "primary_language": primary_language,
        "english_action_note": english_note.strip(),
        "spanish_action_note": spanish_note.strip(),
    }


CAREGIVER_INSTRUCTION = """You are the Family Liaison and Caregiver Communication Specialist for Mississippi Early Intervention.
Your mandate is to translate complex multi-hop routing paths and legal deadlines into warm, respectful,
and completely jargon-free action notes in both English and Spanish.

Key Requirements:
1. Reassure the family that evaluation and IFSP services are covered by Medicaid at zero out-of-pocket cost.
2. Provide transparent step-by-step expectations with confirmed timelines under the 45-day federal clock.
3. Confirm that bilingual (Spanish-speaking) evaluators and coordinators are assigned.
"""


def create_caregiver_comms_agent() -> LlmAgent:
    """Creates the ADK LlmAgent for Bilingual Caregiver Action Notes."""
    return LlmAgent(
        name="CaregiverCommsAgent",
        description="Generates plain-language, bilingual (English/Spanish) caregiver action notes.",
        model=config.model_name,
        instruction=CAREGIVER_INSTRUCTION,
        tools=[format_caregiver_action_note],
    )


CaregiverCommsAgent = create_caregiver_comms_agent()
