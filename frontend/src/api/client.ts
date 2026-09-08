import { client } from "./generated/client.gen";

/**
 * Central handwritten configuration for the generated API client.
 *
 * This module is the single import surface for the SETUP-02 generated client:
 * it applies the existing API base URL convention in one place and re-exports
 * the approved generated entrypoint and its health response types. It is never
 * overwritten by generation (the generator cleans only `./generated/`) and is
 * intentionally unused by production application modules.
 */
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
client.setConfig({ baseUrl });

export { getHealth } from "./generated/index";
export type {
  GetHealthData,
  GetHealthResponse,
  GetHealthResponses,
  HealthResponse,
} from "./generated/index";
