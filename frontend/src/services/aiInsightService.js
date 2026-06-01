const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function getAIInsight(payload) {
  // We use the full endpoint because the backend is structured as /api/ai/insight
  // And the frontend api usually has BASE = "http://localhost:8000/api"
  // Let's just use /api/ai/insight but we need to ensure the base URL is correct.
  // Actually, the simplest is to just use "http://localhost:8000/api/ai/insight" 
  // or fetch directly relative to window.location if proxied.
  
  // To be safe in dev, assuming standard setup:
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  const response = await fetch(`${API_URL}/api/ai/insight`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("AI Insight request failed");
  }

  return response.json();
}
