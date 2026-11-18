#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="first-milestones-agent"
REGION="us-central1"
PROJECT_ID="qwiklabs-gcp-04-5956a6cfcbdf"

echo "Deploying ${SERVICE_NAME} (Full Suite: Multi-Agent ADK + Interactive UI + MCP Server) to Cloud Run in ${REGION}..."

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=${PROJECT_ID},BIGQUERY_DATASET=a4i_early_intervention,STATE_CODE=MS,STATE_FIPS=28,MODEL_NAME=gemini-2.5-flash" \
  --min-instances=1 \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --quiet

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project "${PROJECT_ID}" --region "${REGION}" --format="value(status.url)")

echo "Deployment complete!"
echo "Service URL: ${SERVICE_URL}"
echo "Testing /health endpoint..."
curl -s "${SERVICE_URL}/health"
echo ""
