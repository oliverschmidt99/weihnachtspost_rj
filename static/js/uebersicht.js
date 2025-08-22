// static/js/uebersicht.js

document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById("overview-table");
  const toggler = document.getElementById("column-toggler");
  const noCustomerCell = document.getElementById("no-customer-cell");

  // Stoppt die Ausführung, wenn die Tabelle nicht gefunden wird
  if (!table || !toggler) return;

  const allColumns = [
    { class: "col-id", text: "ID" },
    { class: "col-status", text: "Status" },
    { class: "col-mitarbeiter", text: "Mitarbeiter" },
    { class: "col-anrede", text: "Anrede" },
    { class: "col-titel", text: "Titel" },
    { class: "col-vorname", text: "Vorname" },
    { class: "col-nachname", text: "Nachname" },
    { class: "col-firma1", text: "Firma 1" },
    { class: "col-firma2", text: "Firma 2" },
    { class: "col-funktion", text: "Funktion" },
    { class: "col-abteilung", text: "Abteilung" },
    { class: "col-strasse", text: "Straße" },
    { class: "col-plz", text: "PLZ" },
    { class: "col-ort", text: "Ort" },
    { class: "col-land", text: "Land" },
    { class: "col-anschriftswahl", text: "Anschriftswahl" },
    { class: "col-email", text: "E-Mail" },
    { class: "col-tel-beruflich", text: "Telefon (berufl.)" },
    { class: "col-durchwahl", text: "Durchwahl" },
    { class: "col-mobil", text: "Mobil" },
    { class: "col-fax", text: "Fax" },
    { class: "col-tel-privat", text: "Telefon (privat)" },
    { class: "col-anmerkungen", text: "Anmerkungen" },
    { class: "col-aktionen", text: "Aktionen" },
  ];

  const STORAGE_KEY = "kundenkommunikation_column_visibility";
  let visibility = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};

  function applyVisibility() {
    const theadTr = table.querySelector("thead tr");
    theadTr.innerHTML = "";
    let visibleColumnCount = 0;

    allColumns.forEach((col) => {
      const isVisible = visibility[col.class] !== false;
      if (isVisible) {
        const th = document.createElement("th");
        th.className = col.class;
        th.textContent = col.text;
        theadTr.appendChild(th);
        visibleColumnCount++;
      }
      table.querySelectorAll(`tbody .${col.class}`).forEach((cell) => {
        cell.style.display = isVisible ? "" : "none";
      });
    });

    if (noCustomerCell) {
      noCustomerCell.setAttribute("colspan", visibleColumnCount);
    }
  }

  // Erstellt die Checkboxen zum Ein-/Ausblenden
  allColumns.forEach((col) => {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";

    const isVisibleByDefault = [
      "col-id",
      "col-status",
      "col-mitarbeiter",
      "col-nachname",
      "col-vorname",
      "col-firma1",
      "col-email",
      "col-aktionen",
    ].includes(col.class);

    if (visibility[col.class] === undefined) {
      visibility[col.class] = isVisibleByDefault;
    }
    checkbox.checked = visibility[col.class];

    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(col.text));
    toggler.appendChild(label);

    checkbox.addEventListener("change", () => {
      visibility[col.class] = checkbox.checked;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(visibility));
      applyVisibility();
    });
  });

  // Wende die Sichtbarkeit beim ersten Laden der Seite an
  applyVisibility();
});
