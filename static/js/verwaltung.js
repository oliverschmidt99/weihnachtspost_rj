// static/js/verwaltung.js

document.addEventListener("DOMContentLoaded", () => {
  // Initialisiert die Haupt-Reiter (Mitarbeiter/Kunden)
  initializeCardNavigation("verwaltung-nav", "verwaltung-sektionen");

  // --- Modal-Logik ---

  // Buttons zum Öffnen der Modals
  const addMitarbeiterBtn = document.getElementById("add-mitarbeiter-btn");
  const addKundeBtn = document.getElementById("add-kunde-btn");
  const importKundeBtn = document.getElementById("import-kunde-btn");

  // Modals
  const addMitarbeiterModal = document.getElementById("modal-add-mitarbeiter");
  const addKundeModal = document.getElementById("modal-add-kunde");
  const importKundeModal = document.getElementById("modal-import-kunde");

  // Event Listeners zum Öffnen
  addMitarbeiterBtn.addEventListener("click", () =>
    openModal(addMitarbeiterModal)
  );
  addKundeBtn.addEventListener("click", () => openModal(addKundeModal));
  importKundeBtn.addEventListener("click", () => openModal(importKundeModal));

  // Allen Schließen- und Abbrechen-Buttons die Schließen-Funktion zuweisen
  document
    .querySelectorAll(".modal-close-btn, .modal-cancel-btn")
    .forEach((btn) => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal-overlay");
        closeModal(modal);
      });
    });
});

/**
 * Öffnet ein Modal-Fenster.
 * @param {HTMLElement} modal - Das Modal-Element, das geöffnet werden soll.
 */
function openModal(modal) {
  if (modal) {
    modal.style.display = "flex";
  }
}

/**
 * Schließt ein Modal-Fenster.
 * @param {HTMLElement} modal - Das Modal-Element, das geschlossen werden soll.
 */
function closeModal(modal) {
  if (modal) {
    modal.style.display = "none";
  }
}
