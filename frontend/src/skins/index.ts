export function loadSkin(skin: string) {
  switch (skin) {
    case "afternoon":
      import("./afternoon.css");
      break;
    case "sunset":
      import("./sunset.css");
      break;
    case "morning":
      import("./morning.css");
      break;
    default:
      import("./night.css");
  }
}


