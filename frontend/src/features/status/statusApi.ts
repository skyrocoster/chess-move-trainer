export type HealthResponse = { status: "ok" };

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/health`, { signal });
  if (!response.ok) {
    throw new Error(`Health request failed with HTTP ${response.status}`);
  }
  const body: unknown = await response.json();
  if (!body || typeof body !== "object" || (body as Record<string, unknown>).status !== "ok") {
    throw new Error("Health response was malformed");
  }
  return { status: "ok" };
}
