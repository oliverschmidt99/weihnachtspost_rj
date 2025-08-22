// static/js/forms.js
document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".tag-selector-container")
    .forEach(initializeTagSelection);
  document
    .querySelectorAll(".title-selector-container")
    .forEach(initializeTitleSelection);
});

// --- TITEL-AUSWAHL ---
function initializeTitleSelection(container) {
  const selectedContainer = container.querySelector(".selected-titles");
  const searchInput = container.querySelector(".title-search");
  const checkboxes = container.querySelectorAll(
    '.title-options input[type="checkbox"]'
  );
  const initialTitles = (container.dataset.selectedTitles || "")
    .split(",")
    .filter(Boolean);

  let selectedTitles = [...initialTitles];

  function updateDisplay() {
    selectedContainer.innerHTML = "";
    selectedTitles.forEach((title) => {
      const badge = document.createElement("span");
      badge.className = "tag-badge";
      badge.textContent = title;
      const removeBtn = document.createElement("span");
      removeBtn.className = "remove-tag";
      removeBtn.innerHTML = "&times;";
      removeBtn.addEventListener("click", () => {
        selectedTitles = selectedTitles.filter((t) => t !== title);
        updateCheckboxes();
        updateDisplay();
      });
      badge.appendChild(removeBtn);
      selectedContainer.appendChild(badge);
    });
  }

  function updateCheckboxes() {
    checkboxes.forEach((cb) => {
      cb.checked = selectedTitles.includes(cb.value);
    });
  }

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        if (!selectedTitles.includes(checkbox.value))
          selectedTitles.push(checkbox.value);
      } else {
        selectedTitles = selectedTitles.filter((t) => t !== checkbox.value);
      }
      updateDisplay();
    });
  });

  searchInput.addEventListener("input", () => {
    const filter = searchInput.value.toLowerCase();
    checkboxes.forEach((cb) => {
      const label = cb.parentElement;
      label.style.display = cb.value.toLowerCase().includes(filter)
        ? ""
        : "none";
    });
  });

  updateCheckboxes();
  updateDisplay();
}

// --- TAG-AUSWAHL ---
function initializeTagSelection(container) {
  const displayContainer = container.querySelector(".selected-tags");
  const addButton = container.querySelector(".add-tags-btn");
  const initialTags = (container.dataset.selectedTags || "")
    .split(",")
    .filter(Boolean);

  let currentSelectedTags = [...initialTags];

  function updateDisplay() {
    displayContainer.innerHTML = "";
    currentSelectedTags.forEach((tag) => {
      displayContainer.innerHTML += getTagBadge(tag, true);
    });
  }

  displayContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-tag")) {
      const tagName = e.target.parentElement.dataset.tag;
      currentSelectedTags = currentSelectedTags.filter((t) => t !== tagName);
      updateDisplay();
    }
  });

  addButton.addEventListener("click", async () => {
    await openTagModal(currentSelectedTags, (newTags) => {
      currentSelectedTags = newTags;
      updateDisplay();
    });
  });

  updateDisplay();
}

async function openTagModal(selectedTags, onSave) {
  await loadTags();
  const modal = document.getElementById("tag-modal");
  const listContainer = modal.querySelector("#modal-tag-list");
  const saveBtn = modal.querySelector("#modal-save-btn");
  const cancelBtn = modal.querySelector(".modal-cancel-btn, .modal-close-btn");

  let tempSelectedTags = [...selectedTags];

  listContainer.innerHTML = "";
  allTagsData.categories.forEach((category) => {
    const group = document.createElement("div");
    group.className = "tag-group";
    group.innerHTML = `<strong>${category.name}</strong>`;
    const tagsDiv = document.createElement("div");
    category.tags.forEach((tag) => {
      const badge = document.createElement("span");
      badge.className = "tag-badge";
      badge.textContent = tag.name;
      badge.style.backgroundColor = tag.color;
      badge.style.color = getTextColor(tag.color);
      if (tempSelectedTags.includes(tag.name)) {
        badge.classList.add("selected");
      }
      badge.addEventListener("click", () => {
        badge.classList.toggle("selected");
        if (tempSelectedTags.includes(tag.name)) {
          tempSelectedTags = tempSelectedTags.filter((t) => t !== tag.name);
        } else {
          tempSelectedTags.push(tag.name);
        }
      });
      tagsDiv.appendChild(badge);
    });
    group.appendChild(tagsDiv);
    listContainer.appendChild(group);
  });

  const onSaveClick = () => {
    onSave(tempSelectedTags);
    closeModal(modal);
    cleanup();
  };

  const onCancelClick = () => {
    closeModal(modal);
    cleanup();
  };

  const cleanup = () => {
    saveBtn.removeEventListener("click", onSaveClick);
    cancelBtn.removeEventListener("click", onCancelClick);
  };

  saveBtn.addEventListener("click", onSaveClick);
  cancelBtn.addEventListener("click", onCancelClick);

  openModal(modal);
}
