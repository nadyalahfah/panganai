import { buildApiUrl } from "../api";

export async function getAIInsight(payload) {
  const response = await fetch(buildApiUrl("ai/insight"), {
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
