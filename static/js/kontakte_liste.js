// static/js/kontakte_liste.js
document.addEventListener("DOMContentLoaded", () => {
  const { createApp, ref, computed, watch } = Vue;

  createApp({
    setup() {
      const vorlagen = ref(
        JSON.parse(
          document.getElementById("vorlagen-for-json-data").textContent
        )
      );
      const isAddModalOpen = ref(false);
      const isImportModalOpen = ref(false);
      const newContactData = ref({});
      const activeVorlageId = ref(
        vorlagen.value.length > 0 ? vorlagen.value[0].id : null
      );
      const addModalVorlageId = ref(activeVorlageId.value);

      const activeVorlage = computed(() =>
        vorlagen.value.find((v) => v.id === activeVorlageId.value)
      );
      const addModalVorlage = computed(() =>
        vorlagen.value.find((v) => v.id === addModalVorlageId.value)
      );

      watch(addModalVorlageId, () => {
        newContactData.value = {};
      });

      const openAddModal = () => {
        isAddModalOpen.value = true;
      };
      const closeAddModal = () => {
        isAddModalOpen.value = false;
      };
      const openImportModal = () => {
        isImportModalOpen.value = true;
      };
      const closeImportModal = () => {
        isImportModalOpen.value = false;
      };

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
      };
    },
  }).mount("#kontakte-app");
});
