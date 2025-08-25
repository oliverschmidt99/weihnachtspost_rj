// static/js/settings.js
document.addEventListener("DOMContentLoaded", () => {
  // --- Dark Mode Toggle ---
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.checked =
      document.documentElement.getAttribute("data-theme") === "dark";

    themeToggle.addEventListener("change", () => {
      const newTheme = themeToggle.checked ? "dark" : "light";
      applyTheme(newTheme);
    });
  }

  // --- Vue App für Auswahllisten-Editor ---
  const editorRoot = document.getElementById("selection-options-editor");
  if (editorRoot) {
    const { createApp, ref, onMounted } = Vue;

    createApp({
      setup() {
        const selectionOptions = ref({ options: [] });

        const loadOptions = async () => {
          try {
            const response = await fetch("/api/selection-options");
            if (!response.ok) throw new Error("Netzwerkfehler");
            selectionOptions.value = await response.json();
          } catch (error) {
            console.error("Fehler beim Laden der Auswahllisten:", error);
            alert("Fehler beim Laden der Auswahllisten.");
          }
        };

        const saveOptions = async () => {
          try {
            const response = await fetch("/api/selection-options", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(selectionOptions.value),
            });
            const result = await response.json();
            if (result.success) {
              alert("Auswahllisten erfolgreich gespeichert!");
            } else {
              throw new Error(result.error || "Unbekannter Fehler");
            }
          } catch (error) {
            console.error("Fehler beim Speichern:", error);
            alert(`Fehler beim Speichern: ${error.message}`);
          }
        };

        const addList = () => {
          selectionOptions.value.options.push({
            name: "Neue Liste",
            values: "",
          });
        };

        const removeList = (index) => {
          if (confirm("Möchtest du diese Liste wirklich entfernen?")) {
            selectionOptions.value.options.splice(index, 1);
          }
        };

        onMounted(loadOptions);

        return {
          selectionOptions,
          saveOptions,
          addList,
          removeList,
        };
      },
      compilerOptions: {
        delimiters: ["{[", "]}"],
      },
    }).mount(editorRoot);
  }
});

// Globale Theme-Funktion, falls sie in main.js ist, kann diese hier weg
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}
