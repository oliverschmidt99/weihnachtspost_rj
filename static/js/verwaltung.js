// static/js/verwaltung.js
document.addEventListener("DOMContentLoaded", () => {
  initializeCardNavigation("verwaltung-nav", "verwaltung-sektionen");

  const addMitarbeiterBtn = document.getElementById("add-mitarbeiter-btn");
  const addKundeBtn = document.getElementById("add-kunde-btn");
  const importKundeBtn = document.getElementById("import-kunde-btn");

  const addMitarbeiterModal = document.getElementById("modal-add-mitarbeiter");
  const addKundeModal = document.getElementById("modal-add-kunde");
  const importKundeModal = document.getElementById("modal-import-kunde");

  addMitarbeiterBtn.addEventListener("click", () =>
    openModal(addMitarbeiterModal)
  );
  addKundeBtn.addEventListener("click", () => openModal(addKundeModal));
  importKundeBtn.addEventListener("click", () => openModal(importKundeModal));

  document
    .querySelectorAll(".modal-close-btn, .modal-cancel-btn")
    .forEach((btn) => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal-overlay");
        closeModal(modal);
      });
    });
});
