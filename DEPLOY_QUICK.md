# Quick Deploy to Cloud Run

**Project:** `vibecode-gemini3-competition`  
**Project ID:** `gen-lang-client-0859375571`

## One-Command Deploy

```bash
./deploy.sh
```

This script will:
1. ✅ Set your Google Cloud project
2. ✅ Enable required APIs
3. ✅ Build and deploy to Cloud Run
4. ✅ Show you the live URL

## Manual Deploy (Alternative)

```bash
# 1. Set project
gcloud config set project gen-lang-client-0859375571

# 2. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# 3. Deploy
gcloud run deploy agentqms-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEMO_MODE=true \
  --memory 512Mi \
  --cpu 1

# 4. Get URL
gcloud run services describe agentqms-dashboard \
  --region us-central1 \
  --format='value(status.url)'
```

## With Gemini API Key

```bash
gcloud run deploy agentqms-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEMO_MODE=true,GEMINI_API_KEY=your_key_here \
  --memory 512Mi \
  --cpu 1
```

## View Logs

```bash
gcloud run services logs read agentqms-dashboard \
  --region us-central1 \
  --follow
```

## Update Environment Variables

```bash
gcloud run services update agentqms-dashboard \
  --region us-central1 \
  --update-env-vars GEMINI_API_KEY=new_key_here
```

---

**Need help?** See [DEPLOY.md](DEPLOY.md) for detailed instructions.

