// static/js/settings.js

document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  if (!themeToggle) return;

  // Setzt den Schalter auf den Zustand des aktuell geladenen Themes
  themeToggle.checked =
    document.documentElement.getAttribute("data-theme") === "dark";

  // Fügt den Event-Listener hinzu, der beim Klicken das Theme ändert
  themeToggle.addEventListener("change", () => {
    const newTheme = themeToggle.checked ? "dark" : "light";
    // Ruft die globale Funktion aus main.js auf
    applyTheme(newTheme);
  });
});
