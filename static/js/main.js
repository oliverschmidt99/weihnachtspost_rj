// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  // Theme anwenden, das im Head-Skript gesetzt wurde
  const theme = document.documentElement.getAttribute("data-theme");
  applyTheme(theme);

  // WICHTIG: Diese Funktion steuert die blaue Hervorhebung
  handleNavSlider();

  // Event Listener für andere UI-Elemente
  if (document.getElementById("action-button")) {
    document.getElementById("action-button").addEventListener("click", () => {
      alert("Button wurde geklickt!");
    });
  }

  document.querySelectorAll(".accordion-button").forEach((button) => {
    button.addEventListener("click", () => {
      button.classList.toggle("active");
      const content = button.nextElementSibling;
      content.style.maxHeight = content.style.maxHeight
        ? null
        : content.scrollHeight + "px";
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
    // Kurze Verzögerung, um sicherzustellen, dass alles gerendert ist
    setTimeout(() => {
      slider.style.width = `${activeNavItem.offsetWidth}px`;
      slider.style.left = `${activeNavItem.offsetLeft}px`;
    }, 10);
  }
}
