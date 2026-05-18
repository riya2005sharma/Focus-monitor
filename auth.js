var API = "http://localhost:8000";

async function register() {
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !email || !password) {
        showError("Please fill in all fields");
        return;
    }

    try {
        const res = await fetch(`${API}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.ok) {
            showSuccess("Account created! Redirecting to login...");
            setTimeout(() => window.location.href = "index.html", 1500);
        } else {
            showError(data.detail || "Registration failed");
        }
    } catch (err) {
        showError("Cannot connect to server. Is the backend running?");
    }
}

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        showError("Please fill in all fields");
        return;
    }

    try {
        const res = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("username", data.username);
            window.location.href = "dashboard.html";
        } else {
            showError(data.detail || "Login failed");
        }
    } catch (err) {
        showError("Cannot connect to server. Is the backend running?");
    }
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "index.html";
}

function showError(msg) {
    const el = document.getElementById("error-msg");
    if (el) {
        el.textContent = msg;
        el.style.display = "block";
    }
}

function showSuccess(msg) {
    const el = document.getElementById("success-msg");
    if (el) {
        el.textContent = msg;
        el.style.display = "block";
    }
}

// Protect dashboard — redirect to login if no token
if (window.location.pathname.includes("dashboard") && !localStorage.getItem("token")) {
    window.location.href = "index.html";
}

// Show username on dashboard
if (window.location.pathname.includes("dashboard")) {
    const username = localStorage.getItem("username");
    const el = document.getElementById("welcome-text");
    if (el && username) el.textContent = `Welcome, ${username}!`;
}