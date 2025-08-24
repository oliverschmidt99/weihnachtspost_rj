document.addEventListener("DOMContentLoaded", () => {
  const editorRoot = document.getElementById("vorlage-editor-app");
  if (!editorRoot) {
    return;
  }

  const {
    createApp,
    ref,
    onMounted,
    computed,
    watch,
    nextTick,
    onBeforeUnmount,
  } = Vue;

  const app = createApp({
    setup() {
      const vorlage = ref(
        JSON.parse(document.getElementById("vorlage-data").textContent)
      );
      const allVorlagen = ref(
        JSON.parse(document.getElementById("all-vorlagen-data").textContent)
      );
      const actionUrl = document
        .getElementById("action-url-data")
        .textContent.slice(1, -1);
      const suggestions = ref({ categories: [] });
      const selectionOptions = ref([]);
      const selectedSuggestionCategory = ref(null);
      const viewMode = ref("list");
      const activeModal = ref(null);
      const editedGroup = ref(null);
      const editedGroupIndex = ref(null);
      const deleteTarget = ref(null);
      const deleteMessage = ref("");
      const groupSortable = ref(null);
      const propertySortables = ref({});
      const collapsedGroups = ref({});

      const toggleGroupCollapse = (index) => {
        collapsedGroups.value[index] = !collapsedGroups.value[index];
      };

      const initSortables = () => {
        destroySortables();
        const groupContainer = document.getElementById("group-list-container");
        if (groupContainer) {
          groupSortable.value = new Sortable(groupContainer, {
            animation: 150,
            handle: ".drag-handle",
            onEnd: (event) => {
              const movedItem = vorlage.value.gruppen.splice(
                event.oldIndex,
                1
              )[0];
              vorlage.value.gruppen.splice(event.newIndex, 0, movedItem);
            },
          });
        }
        vorlage.value.gruppen.forEach((gruppe, index) => {
          const propContainer = document.querySelector(
            `.property-list-container[data-group-index='${index}']`
          );
          if (propContainer) {
            propertySortables.value[index] = new Sortable(propContainer, {
              animation: 150,
              handle: ".drag-handle",
              onEnd: (event) => {
                const movedItem = gruppe.eigenschaften.splice(
                  event.oldIndex,
                  1
                )[0];
                gruppe.eigenschaften.splice(event.newIndex, 0, movedItem);
              },
            });
          }
        });
      };

      const destroySortables = () => {
        if (groupSortable.value) groupSortable.value.destroy();
        Object.values(propertySortables.value).forEach((s) => s.destroy());
        groupSortable.value = null;
        propertySortables.value = {};
      };

      onMounted(async () => {
        try {
          const [suggResponse, selOptResponse] = await Promise.all([
            fetch("/api/attribute-suggestions"),
            fetch("/api/selection-options"),
          ]);
          suggestions.value = await suggResponse.json();
          selectionOptions.value = (await selOptResponse.json()).options;
        } catch (error) {
          console.error("Fehler:", error);
        }

        if (viewMode.value === "list") {
          await nextTick();
          initSortables();
        }
      });

      watch(viewMode, async (newMode) => {
        if (newMode === "list") {
          await nextTick();
          initSortables();
        } else {
          destroySortables();
        }
      });

      watch(
        () => vorlage.value.gruppen,
        async () => {
          if (viewMode.value === "list") {
            await nextTick();
            initSortables();
          }
        },
        { deep: true }
      );

      onBeforeUnmount(destroySortables);

      const pageTitle = computed(() =>
        vorlage.value.name
          ? `Vorlage: ${vorlage.value.name}`
          : "Neue Vorlage erstellen"
      );

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

      const saveGroup = () => {
        if (editedGroupIndex.value !== null) {
          vorlage.value.gruppen[editedGroupIndex.value] = editedGroup.value;
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
        const g = {
          name: cat.name,
          eigenschaften: cat.attributes.map((attr) => ({
            name: attr,
            datentyp: "Text",
            optionen: "",
          })),
        };
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
          if (!r.ok) throw new Error("Speichern fehlgeschlagen");
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
        activeModal,
        editedGroup,
        addGroupFromSuggestion,
        addEmptyGruppe,
        openGroupEditModal,
        saveGroup,
        addEigenschaft,
        removeEigenschaft,
        closeModal,
        saveVorlage,
        allVorlagen,
        collapsedGroups,
        toggleGroupCollapse,
      };
    },
  });
  app.config.compilerOptions.delimiters = ["{[", "]}"];
  app.mount(editorRoot);
});
