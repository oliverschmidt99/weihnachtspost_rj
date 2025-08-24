document.addEventListener("DOMContentLoaded", () => {
  const appRoot = document.getElementById("kontakte-app");
  if (!appRoot) {
    return;
  }

  const { createApp, ref, computed, watch, nextTick } = Vue;

  const app = createApp({
    setup() {
      // --- Kompletter State (alt und neu kombiniert) ---
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
      const sortableGroupInstance = ref(null);
      const sortableItemInstances = ref({});

      // Modals
      const isAddModalOpen = ref(false);
      const isImportModalOpen = ref(false);

      // Add Modal
      const newContactData = ref({});
      const addModalVorlageId = ref(activeVorlageId.value);
      const verknuepfungsOptionen = ref({});

      // Import Modal
      const importStep = ref(1);
      const importTargetVorlageId = ref(null);
      const importFile = ref(null);
      const importData = ref({});
      const importMappings = ref({});
      const importError = ref("");

      // --- Computed Properties ---
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
      const importTargetVorlage = computed(() => {
        if (!importTargetVorlageId.value) return null;
        return vorlagen.value.find((v) => v.id === importTargetVorlageId.value);
      });

      // --- Watchers ---
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
        newContactData.value = {};
        if (!newVorlage) return;
        verknuepfungsOptionen.value = {};
        for (const gruppe of newVorlage.gruppen) {
          for (const eigenschaft of gruppe.eigenschaften) {
            if (
              eigenschaft.datentyp === "Verknüpfung" &&
              eigenschaft.optionen.startsWith("vorlage_id:")
            ) {
              const linkedVorlageId = eigenschaft.optionen.split(":")[1];
              try {
                const response = await fetch(
                  `/api/kontakte-by-vorlage/${linkedVorlageId}`
                );
                if (response.ok) {
                  verknuepfungsOptionen.value[eigenschaft.id] =
                    await response.json();
                } else {
                  verknuepfungsOptionen.value[eigenschaft.id] = [];
                }
              } catch (error) {
                console.error(
                  "Fehler beim Laden der Verknüpfungs-Optionen:",
                  error
                );
                verknuepfungsOptionen.value[eigenschaft.id] = [];
              }
            }
          }
        }
      });

      // --- Methoden ---
      const onGroupSort = (event) => {
        const movedItem = activeVorlage.value.gruppen.splice(
          event.oldIndex,
          1
        )[0];
        activeVorlage.value.gruppen.splice(event.newIndex, 0, movedItem);
      };
      const onItemSort = (gruppe, event) => {
        const movedItem = gruppe.eigenschaften.splice(event.oldIndex, 1)[0];
        gruppe.eigenschaften.splice(event.newIndex, 0, movedItem);
      };

      const toggleEditOrderMode = async () => {
        editOrderMode.value = !editOrderMode.value;
        await nextTick();
        if (editOrderMode.value) {
          const groupEl = document.querySelector(".filter-body");
          sortableGroupInstance.value = new Sortable(groupEl, {
            animation: 150,
            onEnd: onGroupSort,
            handle: ".drag-handle",
          });
          activeVorlage.value.gruppen.forEach((gruppe) => {
            const itemEl = document.getElementById(`filter-group-${gruppe.id}`);
            if (itemEl) {
              sortableItemInstances.value[gruppe.id] = new Sortable(itemEl, {
                animation: 150,
                onEnd: (evt) => onItemSort(gruppe, evt),
                handle: ".drag-handle",
              });
            }
          });
        } else {
          if (sortableGroupInstance.value)
            sortableGroupInstance.value.destroy();
          Object.values(sortableItemInstances.value).forEach((instance) =>
            instance.destroy()
          );
          sortableItemInstances.value = {};
        }
      };

      const toggleGroupFilter = (gruppe) => {
        const isAnyActive = gruppe.eigenschaften.some(
          (e) => filterState.value[e.name]
        );
        const newStatus = !isAnyActive;
        gruppe.eigenschaften.forEach((e) => {
          filterState.value[e.name] = newStatus;
        });
      };

      const getGroupToggleState = (gruppe) => {
        if (!gruppe || !gruppe.eigenschaften) return "none";
        const activeCount = gruppe.eigenschaften.filter(
          (e) => filterState.value[e.name]
        ).length;
        if (activeCount === 0) return "none";
        if (activeCount === gruppe.eigenschaften.length) return "all";
        return "some";
      };

      const getToggleIcon = (gruppe) => {
        const state = getGroupToggleState(gruppe);
        if (state === "all") return "/static/img/icon_checkbox_checked.svg";
        if (state === "some") return "/static/img/icon_checkbox_some.svg";
        return "/static/img/icon_checkbox_unchecked.svg";
      };

      const openAddModal = () => (isAddModalOpen.value = true);
      const closeAddModal = () => (isAddModalOpen.value = false);

      const updateField = async (kontakt, fieldName, newValue) => {
        if (kontakt.daten[fieldName] === newValue) return;
        try {
          const response = await fetch(`/api/kontakt/${kontakt.id}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field: fieldName, value: newValue }),
          });
          if (!response.ok) throw new Error("Update fehlgeschlagen");
          const result = await response.json();
          if (result.success) {
            kontakt.daten[fieldName] = newValue;
          }
        } catch (error) {
          console.error("Fehler:", error);
          alert("Speichern fehlgeschlagen.");
        }
      };

      const saveNewContact = async () => {
        if (!addModalVorlageId.value) {
          alert("Bitte eine Vorlage auswählen.");
          return;
        }
        try {
          const response = await fetch("/api/kontakt/neu", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              vorlage_id: addModalVorlageId.value,
              daten: newContactData.value,
            }),
          });
          const result = await response.json();
          if (result.success) {
            const targetVorlage = vorlagen.value.find(
              (v) => v.id === addModalVorlageId.value
            );
            if (targetVorlage) {
              targetVorlage.kontakte.push(result.kontakt);
            }
            closeAddModal();
          } else {
            throw new Error(result.error);
          }
        } catch (error) {
          console.error("Fehler:", error);
          alert("Speichern fehlgeschlagen.");
        }
      };

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
        vorlagen,
        activeVorlageId,
        activeVorlage,
        isFilterVisible,
        filterState,
        editOrderMode,
        isAddModalOpen,
        newContactData,
        addModalVorlageId,
        addModalVorlage,
        verknuepfungsOptionen,
        filteredEigenschaften,
        isImportModalOpen,
        importStep,
        importTargetVorlageId,
        importTargetVorlage,
        importData,
        importMappings,
        importError,

        openAddModal,
        closeAddModal,
        toggleEditOrderMode,
        toggleGroupFilter,
        getGroupToggleState,
        getToggleIcon,
        updateField,
        saveNewContact,
        openImportModal,
        closeImportModal,
        handleFileUpload,
        finalizeImport,
        getExportUrl,
      };
    },
  });

  app.config.compilerOptions.delimiters = ["{[", "]}"];
  app.mount(appRoot);
});
