function renderNav(activePage) {
    var username = localStorage.getItem("username") || "";
    var html = `
    <nav class="navbar">
      <div class="nav-brand">🎯 Focus Monitor</div>
      <div class="nav-links">
        <a href="dashboard.html" class="${activePage === 'dashboard' ? 'nav-active' : ''}">🏠 Dashboard</a>
        <a href="session.html" class="${activePage === 'session' ? 'nav-active' : ''}">▶ Session</a>
        <a href="analytics.html" class="${activePage === 'analytics' ? 'nav-active' : ''}">📊 Analytics</a>
      </div>
      <div class="nav-user">
        <span class="nav-username">👤 ${username}</span>
        <button onclick="logoutNav()" class="nav-logout">Logout</button>
      </div>
    </nav>
  `;
    document.getElementById("navbar").innerHTML = html;
}

function logoutNav() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "index.html";
}