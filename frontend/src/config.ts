export type AppMode = 'staging' | 'production' | 'playground';
export type ApiMode = 'live' | 'mock';
export type Skin =
  | 'night'
  | 'afternoon'
  | 'sunset'
  | 'morning'
  | 'minimalist'
  | 'business';

export interface AppConfig {
  appMode: AppMode;
  apiMode: ApiMode;
  defaultSkin: Skin;
  availableSkins: Skin[];
}

// Support Vite env in browser and Jest (where we polyfill globalThis["import"].meta.env)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const viteEnv: any = (globalThis as any)['import']?.meta?.env ?? {};
const envAppMode = (viteEnv.VITE_APP_MODE as AppMode) || 'staging';
const envApiMode = (viteEnv.VITE_API_MODE as ApiMode) || 'live';
const envDefaultSkin = (viteEnv.VITE_DEFAULT_SKIN as Skin) || 'night';

export const config: AppConfig = {
  appMode: envAppMode,
  apiMode: envApiMode,
  defaultSkin: envDefaultSkin,
  availableSkins: [
    'night',
    'afternoon',
    'sunset',
    'morning',
    'minimalist',
    'business',
  ],
};
