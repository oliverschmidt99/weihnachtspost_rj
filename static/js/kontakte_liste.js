document.addEventListener("DOMContentLoaded", () => {
  const appRoot = document.getElementById("kontakte-app");
  if (!appRoot) {
    return;
  }

  const { createApp, ref, computed, watch, nextTick } = Vue;

  const app = createApp({
    setup() {
      // --- Bestehender State ---
      const vorlagen = ref(
        JSON.parse(
          document.getElementById("vorlagen-for-json-data").textContent
        )
      );
      const activeVorlageId = ref(
        vorlagen.value.length > 0 ? vorlagen.value[0].id : null
      );
      const isFilterVisible = ref(true);
      const filterState = ref({});
      const editOrderMode = ref(false);
      const isAddModalOpen = ref(false);
      const newContactData = ref({});
      const addModalVorlageId = ref(activeVorlageId.value);
      const verknuepfungsOptionen = ref({});

      // --- NEUER State für Import/Export ---
      const isImportModalOpen = ref(false);
      const importStep = ref(1);
      const importTargetVorlageId = ref(null);
      const importFile = ref(null);
      const importData = ref({});
      const importMappings = ref({});
      const importError = ref("");

      // --- Bestehende Computed Properties ---
      const activeVorlage = computed(() => {
        if (!activeVorlageId.value) return null;
        return vorlagen.value.find((v) => v.id === activeVorlageId.value);
      });
      const addModalVorlage = computed(() =>
        vorlagen.value.find((v) => v.id === addModalVorlageId.value)
      );
      const filteredEigenschaften = computed(() => {
        if (!activeVorlage.value) return [];
        return activeVorlage.value.gruppen
          .flatMap((g) => g.eigenschaften)
          .filter((e) => filterState.value[e.name]);
      });

      // --- NEUE Computed Property ---
      const importTargetVorlage = computed(() => {
        if (!importTargetVorlageId.value) return null;
        return vorlagen.value.find((v) => v.id === importTargetVorlageId.value);
      });

      // --- Bestehende Watchers ---
      watch(
        activeVorlage,
        (newVorlage) => {
          if (newVorlage) {
            const newFilterState = {};
            newVorlage.gruppen
              .flatMap((g) => g.eigenschaften)
              .forEach((e) => {
                newFilterState[e.name] = true;
              });
            filterState.value = newFilterState;
          }
        },
        { immediate: true }
      );

      watch(addModalVorlage, async (newVorlage) => {
        // ... (bestehende Logik)
      });

      // --- Bestehende Methoden ---
      const openAddModal = () => (isAddModalOpen.value = true);
      const closeAddModal = () => (isAddModalOpen.value = false);
      // ... (restliche bestehende Methoden)

      // --- NEUE Methoden für Import/Export ---
      const openImportModal = () => {
        importStep.value = 1;
        importData.value = {};
        importMappings.value = {};
        importFile.value = null;
        importError.value = "";
        importTargetVorlageId.value = activeVorlageId.value;
        isImportModalOpen.value = true;
      };

      const closeImportModal = () => (isImportModalOpen.value = false);

      const handleFileUpload = async (event) => {
        importFile.value = event.target.files[0];
        if (!importFile.value || !importTargetVorlageId.value) {
          importError.value =
            "Bitte zuerst eine Vorlage auswählen und dann eine Datei hochladen.";
          return;
        }
        importError.value = "";

        const formData = new FormData();
        formData.append("file", importFile.value);

        try {
          const response = await fetch("/import/upload", {
            method: "POST",
            body: formData,
          });
          const result = await response.json();
          if (!response.ok) {
            throw new Error(
              result.error || "Unbekannter Fehler beim Hochladen"
            );
          }
          importData.value = result;

          // Automatisches Zuordnen von Spalten
          result.headers.forEach((h) => {
            const matchingProp = importTargetVorlage.value.eigenschaften.find(
              (p) => p.name.toLowerCase().trim() === h.toLowerCase().trim()
            );
            if (matchingProp) {
              importMappings.value[h] = matchingProp.name;
            } else {
              importMappings.value[h] = "";
            }
          });
          importStep.value = 2;
        } catch (error) {
          importError.value = `Fehler: ${error.message}`;
        }
      };

      const finalizeImport = async () => {
        try {
          const response = await fetch("/import/finalize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              vorlage_id: importTargetVorlageId.value,
              mappings: importMappings.value,
              original_data: importData.value.original_data,
            }),
          });
          const result = await response.json();
          if (result.success) {
            window.location.href = result.redirect_url;
          } else {
            throw new Error(result.error || "Unbekannter Fehler beim Import.");
          }
        } catch (error) {
          importError.value = `Import fehlgeschlagen: ${error.message}`;
        }
      };

      const getExportUrl = (format) => {
        if (!activeVorlageId.value) return "#";
        return `/export/${activeVorlageId.value}/${format}`;
      };

      return {
        // Bestehende
        vorlagen,
        activeVorlageId,
        activeVorlage,
        isFilterVisible,
        filterState,
        editOrderMode,
        isAddModalOpen,
        openAddModal,
        closeAddModal,
        newContactData,
        addModalVorlageId,
        addModalVorlage,
        verknuepfungsOptionen,
        filteredEigenschaften,
        // Neue
        isImportModalOpen,
        openImportModal,
        closeImportModal,
        importStep,
        importTargetVorlageId,
        importTargetVorlage,
        handleFileUpload,
        importData,
        importMappings,
        importError,
        finalizeImport,
        getExportUrl,
      };
    },
  });

  app.config.compilerOptions.delimiters = ["{[", "]}"];
  app.mount(appRoot);
});
