#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="${GOOGLE_CLOUD_REGION:-europe-west1}"

echo "========================================================================"
echo "  1. Deploying Lightweight Open-Weights Gemma Inference (Ollama)        "
echo "     Scales to Zero (--min-instances=0) on Google Cloud Run             "
echo "========================================================================"
gcloud run deploy gemma-ollama-server \
  --image=ollama/ollama:latest \
  --region="${REGION}" \
  --cpu=4 \
  --memory=8Gi \
  --min-instances=0 \
  --max-instances=2 \
  --port=11434 \
  --allow-unauthenticated

OLLAMA_URL=$(gcloud run services describe gemma-ollama-server --region="${REGION}" --format="value(status.url)")
echo "Gemma Ollama Endpoint: ${OLLAMA_URL}"

echo "========================================================================"
echo "  2. Deploying RailPulse AI (Google ADK + Streamlit) to Cloud Run       "
echo "========================================================================"
gcloud run deploy railpulse-gemma-tracker \
  --source=. \
  --region="${REGION}" \
  --cpu=2 \
  --memory=4Gi \
  --min-instances=0 \
  --max-instances=5 \
  --set-env-vars="OLLAMA_API_BASE=${OLLAMA_URL},GEMMA_MODEL_NAME=ollama_chat/gemma3:4b" \
  --allow-unauthenticated

APP_URL=$(gcloud run services describe railpulse-gemma-tracker --region="${REGION}" --format="value(status.url)")
echo "========================================================================"
echo "  RailPulse AI Live on Google Cloud Run: ${APP_URL}"
echo "========================================================================"
