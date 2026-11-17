#!/usr/bin/env bash
# ==============================================================================
# VPC Service Controls (VPC-SC) Setup & Enforcement Script
# Challenge 04: Agents for Impact 2026 - Early Intervention Data Protection
# ==============================================================================
set -euo pipefail

PROJECT_ID="qwiklabs-gcp-04-5956a6cfcbdf"
PROJECT_NUMBER="195188148189"
REGION="us-central1"
PERIMETER_NAME="early_intervention_data_perimeter"

echo "=== VPC SERVICE CONTROLS DEPLOYMENT FOR BIGQUERY & AGENTS ==="

# 1. Identify Organization and Access Policy
ORG_ID=$(gcloud organizations list --format="value(name)" 2>/dev/null | head -n 1 || true)
if [ -z "$ORG_ID" ]; then
  echo "⚠️ Note: Current sandbox environment has organization-level policies managed upstream."
  echo "Generating the operational commands for the Organization Security Administrator..."
fi

# 2. Command for Org Security Admin to create Access Policy (if not exists)
echo "Step 1: Discover or create Access Policy:"
echo "  POLICY_ID=\$(gcloud access-context-manager policies list --organization=\${ORG_ID} --format='value(name)' | head -n 1)"

# 3. Command to create Access Level for authorized coordinators and Cloud Run egress
echo "Step 2: Create Authorized Access Level:"
cat << 'EOF'
  gcloud access-context-manager levels create authorized_ei_coordinators_level \
    --policy=${POLICY_ID} \
    --title="Authorized Early Intervention Coordinators" \
    --basic-level-spec=security/access_level.yaml
EOF

# 4. Command to deploy Dry-Run Perimeter first (Prevent Breaking Live Agents)
echo "Step 3: Deploy Service Perimeter in DRY-RUN mode to test without breaking active calls:"
cat << EOF
  gcloud access-context-manager perimeters create ${PERIMETER_NAME} \\
    --policy=\${POLICY_ID} \\
    --title="Early Intervention HIPAA & Part C Data Perimeter" \\
    --resources="projects/${PROJECT_NUMBER}" \\
    --restricted-services="bigquery.googleapis.com,aiplatform.googleapis.com" \\
    --enable-vpc-accessible-services \\
    --vpc-allowed-services="bigquery.googleapis.com,aiplatform.googleapis.com" \\
    --dry-run
EOF

# 5. Connect Cloud Run to VPC via Serverless VPC Access & Private Google Access
echo "Step 4: Configure Cloud Run for Private VPC Egress (No Public Transit):"
cat << EOF
  # Ensure Cloud Run sends all API egress via Private Google Access inside the VPC
  gcloud run services update first-milestones-agent \\
    --project="${PROJECT_ID}" \\
    --region="${REGION}" \\
    --vpc-egress=all-traffic
EOF

# 6. Command to Enforce the Perimeter
echo "Step 5: Enforce Perimeter from Dry-Run to Active:"
cat << EOF
  gcloud access-context-manager perimeters commit-dry-run ${PERIMETER_NAME} \\
    --policy=\${POLICY_ID}
EOF

echo "=== Specification ready in security/vpc_sc_perimeter.yaml ==="
