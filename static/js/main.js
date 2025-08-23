// static/js/main.js

// ## GLOBALE INITIALISIERUNG ##
document.addEventListener("DOMContentLoaded", () => {
  handleNavSlider();

  // Event-Listener für alle Modal-Schließ-Buttons
  document
    .querySelectorAll(".modal-close-btn, .modal-cancel-btn")
    .forEach((btn) => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal-overlay");
        if (modal) {
          closeModal(modal);
        }
      });
    });
});

/**
 * Wendet das ausgewählte Theme (hell/dunkel) an und speichert es im Browser.
 * @param {string} theme - Das anzuwendende Theme ('light' or 'dark').
 */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

/**
 * Steuert den animierten Slider in der Hauptnavigation.
 */
function handleNavSlider() {
  const nav = document.getElementById("main-nav");
  if (!nav) return;

  const slider = nav.querySelector(".nav-slider");
  const activeLink = nav.querySelector("a.active");

  if (activeLink) {
    const activeNavItem = activeLink.parentElement;
    // Kurze Verzögerung, damit das Layout berechnet ist
    setTimeout(() => {
      slider.style.width = `${activeNavItem.offsetWidth}px`;
      slider.style.left = `${activeNavItem.offsetLeft}px`;
    }, 50);
  }
}

// Funktionen zum Öffnen und Schließen der Modals
function openModal(modal) {
  if (modal) modal.style.display = "flex";
}
function closeModal(modal) {
  if (modal) modal.style.display = "none";
}
