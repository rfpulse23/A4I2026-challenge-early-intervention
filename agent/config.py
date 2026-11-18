"""Configuration settings for the Early Intervention (First Milestones) Agents."""

import os
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Configuration for Early Intervention Triage Agents."""
    
    # GCP Project & BigQuery settings
    project_id: str = os.getenv("PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-5956a6cfcbdf"))
    bq_dataset: str = os.getenv("BIGQUERY_DATASET", "a4i_early_intervention")
    property_graph_name: str = os.getenv("PROPERTY_GRAPH_NAME", "ReferralGraph")
    
    # Target State (Mississippi defaults)
    state_code: str = os.getenv("STATE_CODE", "MS")
    state_fips: str = os.getenv("STATE_FIPS", "28")
    
    # LLM Settings
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    temperature: float = 0.2
    
    # Statutory & Triage Constants
    idea_part_c_max_wait_days: int = 45
    part_c_age_out_months: int = 36
    
    @property
    def full_graph_path(self) -> str:
        """Returns dataset-qualified property graph identifier."""
        return f"{self.bq_dataset}.{self.property_graph_name}"


config = AgentConfig()
