// static/js/settings.js
document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  if (!themeToggle) return;

  themeToggle.checked =
    document.documentElement.getAttribute("data-theme") === "dark";

  themeToggle.addEventListener("change", () => {
    const newTheme = themeToggle.checked ? "dark" : "light";
    applyTheme(newTheme);
  });
});
