var API = "http://localhost:8000";

let sessionId = null;
let timerInterval = null;
let secondsElapsed = 0;
let isPaused = false;
let plannedSeconds = 0;

function getToken() {
    return localStorage.getItem("token");
}

// Redirect if not logged in
if (!getToken()) {
    window.location.href = "index.html";
}

// Show username
window.addEventListener("DOMContentLoaded", function() {
    const un = localStorage.getItem("username");
    const el = document.getElementById("username-display");
    if (el && un) el.textContent = un;

    // Attach button listener here instead of onclick in HTML
    const startBtn = document.getElementById("start-btn");
    if (startBtn) {
        startBtn.addEventListener("click", startSession);
    }
});

async function startSession() {
    const subjectEl = document.getElementById("subject");
    const durationEl = document.getElementById("duration");

    if (!subjectEl || !durationEl) {
        alert("Form elements not found!");
        return;
    }

    const subject = subjectEl.value.trim();
    const duration = parseInt(durationEl.value);

    if (!subject || !duration || duration < 1) {
        alert("Please enter a subject and valid duration.");
        return;
    }

    const token = getToken();
    if (!token) {
        alert("Not logged in!");
        window.location.href = "index.html";
        return;
    }

    try {
        const res = await fetch(`${API}/session/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ subject: subject, planned_duration: duration })
        });

        const data = await res.json();

        if (!res.ok) {
            alert("Error: " + (data.detail || "Failed to start session"));
            return;
        }

        sessionId = data.session_id;
        plannedSeconds = duration * 60;
        secondsElapsed = 0;
        isPaused = false;

        document.getElementById("setup-panel").style.display = "none";
        document.getElementById("timer-panel").style.display = "block";
        document.getElementById("session-subject-display").textContent = "Studying: " + subject;

        timerInterval = setInterval(() => {
            if (!isPaused) {
                secondsElapsed++;
                updateTimerDisplay();

                if (secondsElapsed >= plannedSeconds) {
                    clearInterval(timerInterval);
                    stopSession("completed");
                }
            }
        }, 1000);

    } catch (err) {
        alert("Cannot connect to server. Is the backend running?\n" + err.message);
    }
}

function updateTimerDisplay() {
    const remaining = plannedSeconds - secondsElapsed;
    const mins = Math.floor(Math.abs(remaining) / 60);
    const secs = Math.abs(remaining) % 60;
    document.getElementById("timer-display").textContent =
        (remaining < 0 ? "-" : "") +
        String(mins).padStart(2, "0") + ":" +
        String(secs).padStart(2, "0");
}

function togglePause() {
    isPaused = !isPaused;
    document.getElementById("pause-btn").textContent = isPaused ? "Resume" : "Pause";
}

async function stopSession(status) {
    clearInterval(timerInterval);
    const actualMinutes = Math.ceil(secondsElapsed / 60);

    try {
        await fetch(`${API}/session/end`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + getToken()
            },
            body: JSON.stringify({
                session_id: sessionId,
                actual_duration: actualMinutes,
                status: status
            })
        });
    } catch (err) {
        console.error("Could not save session:", err);
    }

    document.getElementById("timer-panel").style.display = "none";
    document.getElementById("result-panel").style.display = "block";

    const mins = Math.floor(secondsElapsed / 60);
    const secs = secondsElapsed % 60;
    document.getElementById("result-text").textContent =
        status === "completed" ?
        `Great work! You studied for ${mins}m ${secs}s.` :
        `Session abandoned after ${mins}m ${secs}s.`;
}

function resetSession() {
    sessionId = null;
    secondsElapsed = 0;
    document.getElementById("setup-panel").style.display = "block";
    document.getElementById("result-panel").style.display = "none";
    document.getElementById("subject").value = "";
    document.getElementById("duration").value = "";
}