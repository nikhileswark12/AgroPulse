// Shared frontend helpers for AgroPulse
(function(){
  window.navigate = function(page){
    if(!page) return;
    window.location.assign(page);
  }

  window.showAlert = function(msg, type='info', timeout=4000){
    // Generic alert: looks for #alertBox in page
    const box = document.getElementById('alertBox');
    if(!box) return;
    box.textContent = msg;
    box.className = 'alert ' + (type === 'error' ? 'error' : (type === 'success' ? 'success' : ''));
    box.style.display = 'block';
    setTimeout(()=>{ if(box) box.style.display = 'none'; }, timeout);
  }

  window.setLoading = function(buttonId, state){
    const btn = document.getElementById(buttonId);
    if(!btn) return;
    btn.disabled = state;
    btn.innerHTML = state ? '<span class="spinner"></span>Working...' : btn.getAttribute('data-default') || btn.textContent;
  }

  // Expose a small DOM ready helper
  window.ready = function(fn){
    if(document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn);
  }

})();
