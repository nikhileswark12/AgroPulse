async function loadPredictionMetadata() {
  try {
    const data = await window.fetchJSON('/api/v1/predict/metadata', { noRedirectOn401: true });

    if (!data.success) return;

    window.PREDICTION_META = data;

    // Prediction - Keep the metadata in window.PREDICTION_META but DO NOT blindly 
    // populate select elements here since index.html, prediction.html and comparison.html
    // have their own dynamic cascading dropdown logic.
    // We only populate if the specific elements are completely empty or unmanaged.

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
