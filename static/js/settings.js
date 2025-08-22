// static/js/settings.js

document.addEventListener("DOMContentLoaded", () => {
  // Logik für den Dark Mode Schalter
  const themeToggle = document.getElementById("theme-toggle");

  // Stelle sicher, dass der Schalter den korrekten Zustand hat, wenn die Seite geladen wird
  themeToggle.checked =
    document.documentElement.getAttribute("data-theme") === "dark";

  // Füge den Event Listener hinzu, der beim Klicken das Theme ändert
  themeToggle.addEventListener("change", () => {
    const newTheme = themeToggle.checked ? "dark" : "light";
    applyTheme(newTheme);
  });
});

// Diese Funktion wendet das Theme an und speichert die Auswahl
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}
