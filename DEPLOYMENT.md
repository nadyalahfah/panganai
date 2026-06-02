# Local + Deployment Checklist

## Local development

Backend:

```powershell
cd backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Local backend uses `USE_AZURE_BLOB=false`, so it reads artifacts from `backend/.cache`.

Frontend:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Local frontend should use:

```env
VITE_API_URL=http://localhost:8000
```

## Azure App Service backend

Set these in Azure Portal → App Service → Configuration → Application settings:

```env
USE_AZURE_BLOB=true
AZURE_STORAGE_CONNECTION_STRING=<storage account connection string>
AZURE_BLOB_CONTAINER=paganai-artifacts
CORS_ALLOWED_ORIGINS=https://panganai.vercel.app
```

Also set the artifact blob paths if they differ from `backend/.env.azure.example`.

After deploy/restart, verify:

```powershell
Invoke-WebRequest https://pangan-ai-server-cga4hugfg7che3ce.southeastasia-01.azurewebsites.net/api/health
```

Expected healthy deployment:

```json
{
  "status": "ok",
  "storage_ready": true,
  "storage_error": null,
  "dataset_loaded": true,
  "model_loaded": true,
  "prediction_engine": "catboost"
}
```

If `storage_ready=false`, fix `AZURE_STORAGE_CONNECTION_STRING` first.

## Vercel frontend

Set this in Vercel Project Settings → Environment Variables:

```env
VITE_API_URL=https://pangan-ai-server-cga4hugfg7che3ce.southeastasia-01.azurewebsites.net
```

Redeploy frontend after changing `VITE_API_URL`; Vite embeds env values at build time.
