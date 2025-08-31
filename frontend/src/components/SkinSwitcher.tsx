import React, { useEffect, useMemo, useState } from "react";
import { config, Skin } from "../config";
import { loadSkin } from "../skins";

export default function SkinSwitcher() {
  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const paramSkin = params.get("skin") as Skin | null;

  const initialSkin: Skin = (paramSkin && (config.availableSkins as string[]).includes(paramSkin))
    ? paramSkin
    : config.defaultSkin;

  const [skin, setSkin] = useState<Skin>(initialSkin);

  useEffect(() => {
    try {
      loadSkin(skin);
    } catch (e) {
      // Fallback to default skin if dynamic import fails
      loadSkin(config.defaultSkin);
    }
  }, [skin]);

  const handleChange = (newSkin: Skin) => {
    if ((config.availableSkins as string[]).includes(newSkin)) {
      setSkin(newSkin);
    }
  };

  return (
    <div style={{
      position: "fixed",
      bottom: 10,
      right: 10,
      background: "rgba(0,0,0,0.7)",
      color: "#fff",
      padding: "8px 12px",
      borderRadius: 8,
      fontSize: 14,
      zIndex: 1000
    }}>
      <span style={{ marginRight: 6 }}>Skin:</span>
      {config.availableSkins.map((s) => (
        <button
          key={s}
          onClick={() => handleChange(s as Skin)}
          style={{
            marginLeft: 6,
            background: skin === s ? "#444" : "#222",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            padding: "4px 8px",
            cursor: "pointer"
          }}
        >
          {s}
        </button>
      ))}
    </div>
  );
}


