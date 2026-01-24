async function loadPredictionMetadata() {
  try {
    const res = await fetch('/api/predict/metadata');
    const data = await res.json();

    if (!data.success) return;

    window.PREDICTION_META = data;

    // Index
    populateIfExists("indexCrop", data.crops);
    populateIfExists("indexLocation", data.districts);

    // Prediction
    populateIfExists("cropSelect", data.crops);
    populateIfExists("stateSelect", data.states);
    populateIfExists("districtSelect", data.districts);

    // Comparison
    populateIfExists("compareCrop", data.crops);
    populateIfExists("compareLocation", data.districts);

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
