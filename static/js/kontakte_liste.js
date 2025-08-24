document.addEventListener("DOMContentLoaded", () => {
  const { createApp, ref, computed, watch, nextTick } = Vue;

  const app = createApp({
    setup() {
      // Kompletter State
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
      const isAddModalOpen = ref(false);
      const isImportModalOpen = ref(false);
      const newContactData = ref({});
      const addModalVorlageId = ref(activeVorlageId.value);

      // Computed Properties
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

      // Watchers
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

      watch(addModalVorlageId, () => {
        newContactData.value = {};
      });

      // Methoden
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
      const openImportModal = () => (isImportModalOpen.value = true);
      const closeImportModal = () => (isImportModalOpen.value = false);

      const updateField = async (kontakt, fieldName, newValue) => {
        if (kontakt.daten[fieldName] === newValue) return;
        try {
          const response = await fetch(`/api/kontakt/${kontakt.id}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field: fieldName, value: newValue }),
          });
          const result = await response.json();
          if (result.success) {
            kontakt.daten[fieldName] = newValue;
          } else {
            throw new Error(result.error);
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

      // Der vollständige Return-Block
      return {
        vorlagen,
        activeVorlageId,
        activeVorlage,
        addModalVorlageId,
        addModalVorlage,
        newContactData,
        isAddModalOpen,
        isImportModalOpen,
        openAddModal,
        closeAddModal,
        openImportModal,
        closeImportModal,
        updateField,
        saveNewContact,
        isFilterVisible,
        filterState,
        filteredEigenschaften,
        toggleGroupFilter,
        getGroupToggleState,
        getToggleIcon,
        editOrderMode,
        toggleEditOrderMode,
      };
    },
  });

  app.config.compilerOptions.delimiters = ["{[", "]}"];
  app.mount("#kontakte-app");
});
