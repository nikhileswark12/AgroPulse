async function loadPredictionMetadata() {
  try {
    const data = await window.fetchJSON('/api/v1/predict/metadata', { noRedirectOn401: true });

    if (!data.success) return;

    window.PREDICTION_META = data;

    // Index
    populateIfExists("indexCrop", data.supported_crops);
    populateIfExists("indexLocation", data.supported_districts);

    // Prediction
    populateIfExists("cropSelect", data.supported_crops);
    populateIfExists("stateSelect", data.supported_states);
    populateIfExists("districtSelect", data.supported_districts);

    // Comparison
    populateIfExists("compareCrop", data.supported_crops);
    populateIfExists("compareLocation", data.supported_districts);

  } catch (err) {
    console.error("Failed to load prediction metadata", err);
  }
}

function populateIfExists(id, items) {
  const el = document.getElementById(id);
  if (!el) return;

  el.innerHTML = `<option disabled selected>Select</option>`;
  items.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item;
    opt.textContent = item;
    el.appendChild(opt);
  });
}

document.addEventListener("DOMContentLoaded", loadPredictionMetadata);
