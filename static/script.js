
document.addEventListener("DOMContentLoaded", () => {

    const gestureElement = document.getElementById("current-gesture");
    const gestureStat = document.getElementById("gesture-stat");
    const handCount = document.getElementById("hand-count");
    const fpsElement = document.getElementById("fps");

    const cameraStatus = document.getElementById("camera-status");
    const statusDot = document.getElementById("status-dot");
    const cameraError = document.getElementById("camera-error");

    const historyList = document.getElementById("history-list");
    const gestureDescription = document.getElementById("gesture-description");
    const cameraFeed = document.getElementById("camera-feed");

    if (!gestureElement) return;

    const descriptions = {
        "LIKE": "A positive thumbs-up gesture detected.",
        "DISLIKE": "A thumbs-down gesture detected.",
        "OK": "The OK hand gesture was recognized.",
        "PEACE": "A peace sign gesture was recognized.",
        "CALL ME": "A call-me gesture was recognized.",
        "STOP": "A stop gesture was recognized.",
        "FORWARD": "A forward movement gesture was recognized.",
        "LEFT": "A left direction gesture was recognized.",
        "RIGHT": "A right direction gesture was recognized.",
        "I LOVE YOU": "The I Love You gesture was recognized.",
        "NO GESTURE": "Waiting for your next gesture..."
    };

    function updateHistory(history) {

        historyList.innerHTML = "";

        if (!history || history.length === 0) {

            historyList.innerHTML =
                '<p class="empty-state">Your detected gestures will appear here.</p>';

            return;
        }

        history.forEach(item => {

            const row = document.createElement("div");
            row.className = "history-item";

            const gesture = document.createElement("strong");
            gesture.textContent = item.gesture;

            const time = document.createElement("span");
            time.textContent = item.time;

            row.appendChild(gesture);
            row.appendChild(time);

            historyList.appendChild(row);
        });
    }

    async function updateDashboard() {

        try {

            const response = await fetch("/api/stats", {
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error("Unable to retrieve camera data.");
            }

            const data = await response.json();

            gestureElement.textContent = data.gesture;
            gestureStat.textContent = data.gesture;

            handCount.textContent = data.hands;
            fpsElement.textContent = data.fps;

            gestureDescription.textContent =
                descriptions[data.gesture] || "Gesture recognized.";

            updateHistory(data.history);

            if (data.active) {

                cameraStatus.textContent = "Camera active";
                statusDot.classList.remove("offline");

                cameraError.style.display = "none";

            } else {

                cameraStatus.textContent = "Camera offline";
                statusDot.classList.add("offline");

                cameraError.textContent =
                    data.error || "Waiting for camera...";

                cameraError.style.display = "block";
            }

        } catch (error) {

            cameraStatus.textContent = "Connection error";
            statusDot.classList.add("offline");

            cameraError.textContent = "Unable to connect to camera.";
            cameraError.style.display = "block";

        }
    }

    cameraFeed.addEventListener("error", () => {

        cameraError.textContent =
            "Camera stream unavailable. Check webcam permissions and connection.";

        cameraError.style.display = "block";
    });

    updateDashboard();

    setInterval(updateDashboard, 1000);

});
