import { apiGet, apiPost } from "./client";
import type { LiveEvent } from "../types";

export const eventsApi = {
  list: () => apiGet<{ data: LiveEvent[] }>("/events"),
  create: (body: string) => apiPost<LiveEvent>("/events", { body }),
};
