document.addEventListener("DOMContentLoaded", () => {
  const appRoot = document.getElementById("kontakte-app");
  if (!appRoot) {
    return;
  }

  const { createApp, ref, computed, watch, nextTick } = Vue;

  const app = createApp({
    setup() {
      // ... (bestehende setup-Logik bleibt erhalten) ...
      const isImportModalOpen = ref(false);
      const importStep = ref(1);
      const importTargetVorlageId = ref(null);
      const importFile = ref(null);
      const importData = ref({});
      const importMappings = ref({});
      const importError = ref("");

      const importTargetVorlage = computed(() => {
        if (!importTargetVorlageId.value) return null;
        return vorlagen.value.find((v) => v.id === importTargetVorlageId.value);
      });

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
            throw new Error(result.error || "Unbekannter Fehler");
          }
          importData.value = result;
          // Auto-mapping versuchen
          result.headers.forEach((h) => {
            const matchingProp = importTargetVorlage.value.eigenschaften.find(
              (p) => p.name.toLowerCase() === h.toLowerCase()
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
            throw new Error(result.error);
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
        // ... (alle bestehenden return-Werte) ...
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
