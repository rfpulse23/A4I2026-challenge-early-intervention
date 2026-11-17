"""BigQuery Client helper for executing ISO GQL property graph and SQL queries."""

import logging
from typing import Any, Dict, List, Optional
from google.cloud import bigquery
from agent.config import config

logger = logging.getLogger(__name__)


class BigQueryHelper:
    """Helper for BigQuery operations, ISO GQL queries, and schema-safe data retrieval."""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or config.project_id
        self._client: Optional[bigquery.Client] = None

    @property
    def client(self) -> bigquery.Client:
        """Lazily initialize BigQuery client."""
        if self._client is None:
            self._client = bigquery.Client(project=self.project_id)
        return self._client

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executes a SQL or ISO GQL query and returns results as dictionaries."""
        try:
            job = self.client.query(query)
            results = job.result()
            rows = [dict(row.items()) for row in results]
            return rows
        except Exception as e:
            logger.warning(f"BigQuery query execution encountered: {e}. Executing with graph query wrapper.")
            raise e


bq_helper = BigQueryHelper()
