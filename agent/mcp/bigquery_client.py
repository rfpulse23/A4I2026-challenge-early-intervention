"""
BigQuery Client and Query Service for Early Intervention Property Graph and Tables.
Connects directly to dataset: qwiklabs-gcp-04-5956a6cfcbdf.a4i_early_intervention
Provides seamless fallback to local Parquet/DuckDB if Cloud permissions are scoped read-only.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-5956a6cfcbdf")
DATASET_ID = "a4i_early_intervention"

# Try initializing Google Cloud BigQuery client
try:
    from google.cloud import bigquery
    bq_client = bigquery.Client(project=PROJECT_ID)
except Exception as e:
    bq_client = None

def execute_bq_query(query: str) -> Optional[pd.DataFrame]:
    """Attempts to execute SQL or ISO GQL query on Google BigQuery."""
    if not bq_client:
        return None
    try:
        query_job = bq_client.query(query)
        return query_job.to_dataframe()
    except Exception as e:
        # Falls back gracefully if bigquery.jobs.create is restricted for current SA
        return None

def query_care_nodes(state_code: str = "MS") -> pd.DataFrame:
    """Queries pediatric and early intervention providers."""
    sql = f"""
    SELECT 
        provider_id, synthetic_organization_name, node_role,
        bilingual_services_listed, accepts_medicaid, part_c_vendor_enrolled,
        median_internal_wait_days, active_waitlist_count, latitude, longitude
    FROM `{PROJECT_ID}.{DATASET_ID}.pediatric_and_ei_provider_directory`
    WHERE state_code = '{state_code}'
    """
    df = execute_bq_query(sql)
    if df is not None:
        return df
    
    # Local fallback
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "pediatric_and_ei_provider_directory.parquet"
    local_df = pd.read_parquet(data_path)
    return local_df[local_df["state_code"] == state_code]

def query_referral_logs(state_code: str = "MS", case_chain_id: Optional[str] = None) -> pd.DataFrame:
    """Queries deidentified Part C multi-hop referral logs."""
    where_extra = f"AND case_chain_id = '{case_chain_id}'" if case_chain_id else ""
    sql = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.deidentified_part_c_referral_logs`
    WHERE state_code = '{state_code}' {where_extra}
    ORDER BY case_chain_id, hop_sequence
    """
    df = execute_bq_query(sql)
    if df is not None:
        return df
    
    # Local fallback
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "deidentified_part_c_referral_logs.parquet"
    local_df = pd.read_parquet(data_path)
    res = local_df[local_df["state_code"] == state_code]
    if case_chain_id:
        res = res[res["case_chain_id"] == case_chain_id]
    return res

def query_tract_demographics(tract_geoid: str) -> pd.DataFrame:
    """Queries ACS under-5 tract demographics."""
    sql = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.acs_under5_tract_demographics`
    WHERE census_tract_geoid = '{tract_geoid}'
    """
    df = execute_bq_query(sql)
    if df is not None:
        return df
    
    # Local fallback
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "acs_under5_tract_demographics.parquet"
    local_df = pd.read_parquet(data_path)
    return local_df[local_df["census_tract_geoid"] == tract_geoid]

def query_tract_transit_guardrails(tract_geoid: str) -> pd.DataFrame:
    """Queries BigQuery table: tract_transit_guardrails for transit risk indicators."""
    sql = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.tract_transit_guardrails`
    WHERE census_tract_geoid = '{tract_geoid}'
    """
    df = execute_bq_query(sql)
    if df is not None and not df.empty:
        return df
    
    # Fallback to local Parquet table
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "tract_transit_guardrails.parquet"
    if data_path.exists():
        local_df = pd.read_parquet(data_path)
        matched = local_df[local_df["census_tract_geoid"] == tract_geoid]
        if not matched.empty:
            return matched
            
    # Fallback to acs demographics
    demog_path = Path(__file__).resolve().parent.parent.parent / "data" / "acs_under5_tract_demographics.parquet"
    demog_df = pd.read_parquet(demog_path)
    return demog_df[demog_df["census_tract_geoid"] == tract_geoid]
