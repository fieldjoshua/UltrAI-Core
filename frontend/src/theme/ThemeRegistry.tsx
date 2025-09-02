import React, { createContext, useContext, useEffect } from "react";
import { config, Skin } from "../config";

interface ThemeContextProps {
  skin: Skin;
  setSkin: (skin: Skin) => void;
}

const ThemeContext = createContext<ThemeContextProps | undefined>(undefined);

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeRegistry");
  return ctx;
};

interface ThemeRegistryProps {
  skin: Skin;
  setSkin: (skin: Skin) => void;
  children: React.ReactNode;
}

export const ThemeRegistry: React.FC<ThemeRegistryProps> = ({ skin, setSkin, children }) => {
  useEffect(() => {
    document.documentElement.setAttribute("data-skin", skin);
    document.documentElement.setAttribute("data-app-mode", config.appMode);
  }, [skin]);

  return (
    <ThemeContext.Provider value={{ skin, setSkin }}>
      {children}
    </ThemeContext.Provider>
  );
}; 
