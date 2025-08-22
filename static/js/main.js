// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  // Theme anwenden, das im Head-Skript gesetzt wurde
  const theme = document.documentElement.getAttribute("data-theme");
  applyTheme(theme);

  // Initialisiert die blaue Hervorhebung in der Navigation
  handleNavSlider();

  // Initialisiert die Kachel-Navigation (Tabs) für die Verwaltungsseite
  initializeCardNavigation("verwaltung-nav", "verwaltung-sektionen");
  initializeCardNavigation("kunden-nav", "kunden-sektionen");

  // Initialisiert die Akkordeon-Buttons (aufklappbare Menüs)
  document.querySelectorAll(".accordion-button").forEach((button) => {
    button.addEventListener("click", () => {
      button.classList.toggle("active");
      const content = button.nextElementSibling;
      if (content.style.maxHeight) {
        content.style.maxHeight = null;
      } else {
        content.style.maxHeight = content.scrollHeight + "px";
      }
    });
  });
});

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

function handleNavSlider() {
  const nav = document.getElementById("main-nav");
  if (!nav) return;
  const slider = nav.querySelector(".nav-slider");
  const activeNavItem = nav.querySelector(
    ".nav-item > a.active"
  )?.parentElement;

  if (activeNavItem) {
    setTimeout(() => {
      slider.style.width = `${activeNavItem.offsetWidth}px`;
      slider.style.left = `${activeNavItem.offsetLeft}px`;
    }, 10);
  }
}

// Diese Funktion steuert die Kachel-Navigation
function initializeCardNavigation(navId, sectionContainerId) {
  const cards = document.querySelectorAll(`#${navId} .card`);
  const sections = document.querySelectorAll(
    `#${sectionContainerId} .config-section`
  );
  if (cards.length === 0) return;

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      // Deaktiviere alle Sektionen und Kacheln
      sections.forEach((s) => s.classList.remove("active"));
      cards.forEach((c) => c.classList.remove("active"));

      // Aktiviere die Ziel-Sektion und die geklickte Kachel
      const targetElement = document.getElementById(card.dataset.target);
      if (targetElement) {
        targetElement.classList.add("active");
      }
      card.classList.add("active");
    });
  });
}
