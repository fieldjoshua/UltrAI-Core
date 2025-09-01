export type AppMode = "staging" | "production" | "playground";
export type ApiMode = "live" | "mock";
export type Skin = "night" | "afternoon" | "sunset" | "morning" | "minimalist" | "business";

export interface AppConfig {
  appMode: AppMode;
  apiMode: ApiMode;
  defaultSkin: Skin;
  availableSkins: Skin[];
}

const envAppMode = (import.meta.env.VITE_APP_MODE as AppMode) || "staging";
const envApiMode = (import.meta.env.VITE_API_MODE as ApiMode) || "live";
const envDefaultSkin = (import.meta.env.VITE_DEFAULT_SKIN as Skin) || "night";

export const config: AppConfig = {
  appMode: envAppMode,
  apiMode: envApiMode,
  defaultSkin: envDefaultSkin,
  availableSkins: ["night", "afternoon", "sunset", "morning", "minimalist", "business"],
};


