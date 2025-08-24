// static/js/main.js
document.addEventListener("DOMContentLoaded", () => {
  handleNavSlider();

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

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

function handleNavSlider() {
  const nav = document.getElementById("main-nav");
  if (!nav) return;

  const slider = nav.querySelector(".nav-slider");
  const activeLink = nav.querySelector("a.active");

  if (activeLink) {
    const activeNavItem = activeLink.parentElement;
    setTimeout(() => {
      slider.style.width = `${activeNavItem.offsetWidth}px`;
      slider.style.left = `${activeNavItem.offsetLeft}px`;
    }, 50);
  }
}

function openModal(modal) {
  if (modal) modal.style.display = "flex";
}
function closeModal(modal) {
  if (modal) modal.style.display = "none";
}
