window.fetchJSON = async function(url, options = {}) {
  const res = await fetch(url, options);
  
  if (res.status === 401 && !options.noRedirectOn401) {
    const currentPath = window.location.pathname;
    window.location.href = '/login?returnTo=' + encodeURIComponent(currentPath);
    return new Promise(() => {}); // Wait for redirect
  }
  
  if (res.status === 429) {
    throw { message: "Too many requests — please wait a moment and try again", status: 429 };
  }
  
  if (res.status === 400) {
    let data = {};
    try {
      data = await res.json();
    } catch (e) {
      // ignore JSON parse error
    }
    throw { message: data.error || data.message || "Bad request", status: 400, data };
  }
  
  if (res.status === 500) {
    throw { message: "Server error — please try again later", status: 500 };
  }
  
  if (!res.ok) {
    let msg = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data.message) msg = data.message;
      if (data.error) msg = data.error;
    } catch (e) {}
    throw { message: msg, status: res.status };
  }
  
  return await res.json();
};
