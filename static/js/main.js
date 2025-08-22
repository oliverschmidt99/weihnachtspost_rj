// static/js/main.js

// ## GLOBALE INITIALISIERUNG ##
// Wird ausgeführt, sobald die Grundstruktur der Seite geladen ist.
document.addEventListener("DOMContentLoaded", () => {
  // Initialisiert die blaue Hervorhebung in der Hauptnavigation
  handleNavSlider();

  // Initialisiert alle Akkordeon-Elemente (aufklappbare Menüs) auf der Seite
  initializeAccordion();
});

// ## GLOBALE FUNKTIONEN (auf allen Seiten verfügbar) ##

/**
 * Wendet das ausgewählte Theme (hell/dunkel) an und speichert es im Browser.
 * @param {string} theme - Das anzuwendende Theme ('light' or 'dark').
 */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

/**
 * Steuert den animierten blauen Slider in der Hauptnavigation.
 */
function handleNavSlider() {
  const nav = document.getElementById("main-nav");
  if (!nav) return; // Funktion beenden, wenn keine Navigation da ist

  const slider = nav.querySelector(".nav-slider");
  const activeNavItem = nav.querySelector(
    ".nav-item > a.active"
  )?.parentElement;

  if (activeNavItem) {
    // Kurze Verzögerung, um sicherzustellen, dass alles korrekt gerendert wurde
    setTimeout(() => {
      slider.style.width = `${activeNavItem.offsetWidth}px`;
      slider.style.left = `${activeNavItem.offsetLeft}px`;
    }, 10);
  }
}

/**
 * Sucht nach allen Akkordeon-Buttons und fügt die Klick-Funktionalität hinzu.
 */
function initializeAccordion() {
  document.querySelectorAll(".accordion-button").forEach((button) => {
    button.addEventListener("click", () => {
      const content = button.nextElementSibling;
      button.classList.toggle("active");

      // Öffnen oder schließen durch Setzen der maximalen Höhe
      if (content.style.maxHeight) {
        content.style.maxHeight = null;
      } else {
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });
}

/**
 * Steuert die Kachel-Navigation (Tabs), eine wiederverwendbare UI-Komponente.
 * @param {string} navId Die ID des Containers mit den klickbaren Kacheln.
 * @param {string} sectionContainerId Die ID des Containers, dessen Sektionen gesteuert werden.
 */
function initializeCardNavigation(navId, sectionContainerId) {
  const cards = document.querySelectorAll(`#${navId} .card`);
  const sections = document.querySelectorAll(
    `#${sectionContainerId} .config-section`
  );
  if (cards.length === 0) return;

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      sections.forEach((s) => s.classList.remove("active"));
      cards.forEach((c) => c.classList.remove("active"));

      const targetElement = document.getElementById(card.dataset.target);
      if (targetElement) {
        targetElement.classList.add("active");
      }
      card.classList.add("active");
    });
  });
}
