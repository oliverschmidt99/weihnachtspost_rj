// static/js/vorlage_editor.js
document.addEventListener("DOMContentLoaded", () => {
  const { createApp, ref, onMounted, computed } = Vue;

  createApp({
    setup() {
      const vorlage = ref(
        JSON.parse(document.getElementById("vorlage-data").textContent)
      );
      const allVorlagenRaw = JSON.parse(
        document.getElementById("all-vorlagen-data").textContent
      );
      const actionUrl = document.getElementById("action-url-data").textContent;

      const allVorlagen = ref(allVorlagenRaw);
      const suggestions = ref({ categories: [] });
      const selectionOptions = ref([]);
      const selectedSuggestionCategory = ref(null);
      const viewMode = ref("tile");
      const collapsedGroups = ref({});
      const activeModal = ref(null);
      const editedGroup = ref(null);
      const editedGroupIndex = ref(null);
      const deleteTarget = ref(null);
      const deleteMessage = ref("");

      onMounted(async () => {
        try {
          const [suggResponse, selOptResponse] = await Promise.all([
            fetch("/api/attribute-suggestions"),
            fetch("/api/selection-options"),
          ]);
          suggestions.value = await suggResponse.json();
          selectionOptions.value = (await selOptResponse.json()).options;
        } catch (error) {
          console.error("Fehler beim Laden der Daten:", error);
        }
      });

      const pageTitle = computed(() =>
        vorlage.value.name
          ? `Vorlage: ${vorlage.value.name}`
          : "Neue Vorlage erstellen"
      );
      const toggleGroupCollapse = (index) => {
        collapsedGroups.value[index] = !collapsedGroups.value[index];
      };
      const closeModal = () => {
        activeModal.value = null;
        editedGroup.value = null;
        editedGroupIndex.value = null;
      };
      const openGroupEditModal = (index) => {
        editedGroupIndex.value = index;
        editedGroup.value = JSON.parse(
          JSON.stringify(vorlage.value.gruppen[index])
        );
        activeModal.value = "groupEdit";
      };
      const openDeleteModal = (type, index1) => {
        deleteTarget.value = { type, index1 };
        deleteMessage.value = "Möchten Sie diese Gruppe wirklich löschen?";
        activeModal.value = "delete";
      };
      const saveGroup = () => {
        if (editedGroupIndex.value !== null) {
          vorlage.value.gruppen[editedGroupIndex.value] = editedGroup.value;
        }
        closeModal();
      };
      const confirmDelete = () => {
        const { type, index1 } = deleteTarget.value;
        if (type === "gruppe") {
          vorlage.value.gruppen.splice(index1, 1);
        }
        closeModal();
      };
      const addEigenschaft = () => {
        editedGroup.value.eigenschaften.push({
          name: "",
          datentyp: "Text",
          optionen: "",
        });
      };
      const removeEigenschaft = (index) => {
        editedGroup.value.eigenschaften.splice(index, 1);
      };
      const addGroupFromSuggestion = () => {
        if (!selectedSuggestionCategory.value) return;
        const cat = selectedSuggestionCategory.value;
        const g = { name: cat.name, eigenschaften: [] };
        cat.attributes.forEach((attr) => {
          let dt = "Text";
          if (attr.toLowerCase().includes("datum")) dt = "Datum";
          if (
            attr.toLowerCase().includes("anrede") ||
            attr.toLowerCase().includes("status")
          )
            dt = "Auswahl";
          g.eigenschaften.push({ name: attr, datentyp: dt, optionen: "" });
        });
        vorlage.value.gruppen.push(g);
        selectedSuggestionCategory.value = null;
      };
      const addEmptyGruppe = () => {
        vorlage.value.gruppen.push({ name: "Neue Gruppe", eigenschaften: [] });
      };
      const saveVorlage = async () => {
        try {
          const r = await fetch(actionUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(vorlage.value),
          });
          if (!r.ok) throw new Error("Fehler");
          const res = await r.json();
          if (res.redirect_url) window.location.href = res.redirect_url;
        } catch (e) {
          alert("Speichern fehlgeschlagen.");
        }
      };

      return {
        vorlage,
        suggestions,
        selectionOptions,
        pageTitle,
        selectedSuggestionCategory,
        viewMode,
        collapsedGroups,
        toggleGroupCollapse,
        activeModal,
        editedGroup,
        deleteMessage,
        addGroupFromSuggestion,
        addEmptyGruppe,
        openGroupEditModal,
        saveGroup,
        addEigenschaft,
        removeEigenschaft,
        openDeleteModal,
        confirmDelete,
        closeModal,
        saveVorlage,
        allVorlagen,
      };
    },
  }).mount("#vorlage-editor-app");
});
