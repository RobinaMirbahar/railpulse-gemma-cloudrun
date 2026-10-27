#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="${GOOGLE_CLOUD_REGION:-europe-west1}"
SERVICE_NAME="railpulse-gemma"

echo "========================================================================"
echo "  Deploying RailPulse AI (Gemma + Google ADK + Streamlit) to Cloud Run  "
echo "  Project: ${PROJECT_ID} | Region: ${REGION} | Scale-to-Zero Enabled    "
echo "========================================================================"

gcloud run deploy "${SERVICE_NAME}" \
  --source=. \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=5 \
  --port=8080 \
  --quiet

APP_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)")
echo "========================================================================"
echo "  ✅ RailPulse AI Live on Google Cloud Run:"
echo "  🌐 ${APP_URL}"
echo "========================================================================"
