
document.addEventListener("DOMContentLoaded", () => {

    // Dashboard elements
    const gestureElement = document.getElementById("current-gesture");
    const gestureStat = document.getElementById("gesture-stat");
    const handCount = document.getElementById("hand-count");
    const fpsElement = document.getElementById("fps");

    const cameraStatus = document.getElementById("camera-status");
    const statusDot = document.getElementById("status-dot");
    const cameraError = document.getElementById("camera-error");
    const cameraFeed = document.getElementById("camera-feed");

    const historyList = document.getElementById("history-list");
    const gestureDescription = document.getElementById("gesture-description");

    // Stop if this script is loaded on a page without the dashboard
    if (!gestureElement) return;

    // Gesture descriptions
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

    let previousHistory = "";
    let isUpdating = false;

    // Update camera connection indicator
    function setCameraStatus(active, message = "") {

        if (cameraStatus) {
            cameraStatus.textContent = active
                ? "Camera active"
                : "Camera offline";
        }

        if (statusDot) {
            statusDot.classList.toggle("offline", !active);
        }

        if (cameraError) {
            if (active) {
                cameraError.style.display = "none";
            } else {
                cameraError.textContent = message || "Waiting for camera...";
                cameraError.style.display = "block";
            }
        }
    }

    // Update gesture history
    function updateHistory(history) {

        if (!historyList) return;

        const safeHistory = Array.isArray(history) ? history : [];
        const historyKey = JSON.stringify(safeHistory);

        // Avoid rebuilding the list if nothing changed
        if (historyKey === previousHistory) return;

        previousHistory = historyKey;
        historyList.replaceChildren();

        if (safeHistory.length === 0) {

            const emptyMessage = document.createElement("p");
            emptyMessage.className = "empty-state";
            emptyMessage.textContent =
                "Your detected gestures will appear here.";

            historyList.appendChild(emptyMessage);
            return;
        }

        safeHistory.forEach((item) => {

            const row = document.createElement("div");
            row.className = "history-item";

            const gesture = document.createElement("strong");
            gesture.textContent = item.gesture || "Unknown gesture";

            const time = document.createElement("span");
            time.textContent = item.time || "";

            row.appendChild(gesture);
            row.appendChild(time);

            historyList.appendChild(row);
        });
    }

    // Fetch and update dashboard information
    async function updateDashboard() {

        // Prevent overlapping requests
        if (isUpdating) return;

        isUpdating = true;

        try {

            const response = await fetch("/api/stats", {
                method: "GET",
                cache: "no-store",
                headers: {
                    "Accept": "application/json"
                }
            });

            if (!response.ok) {
                throw new Error("Unable to retrieve camera data.");
            }

            const data = await response.json();

            // Gesture information
            const gesture = data.gesture || "NO GESTURE";

            gestureElement.textContent = gesture;

            if (gestureStat) {
                gestureStat.textContent = gesture;
            }

            if (gestureDescription) {
                gestureDescription.textContent =
                    descriptions[gesture] || "Gesture recognized.";
            }

            // Camera statistics
            if (handCount) {
                handCount.textContent = Number(data.hands) || 0;
            }

            if (fpsElement) {
                fpsElement.textContent = (Number(data.fps) || 0).toFixed(1);
            }

            // Detection history
            updateHistory(data.history);

            // Camera status
            if (data.active) {
                setCameraStatus(true);
            } else {
                setCameraStatus(false, data.error);
            }

        } catch (error) {

            console.error("Dashboard update error:", error);

            setCameraStatus(
                false,
                "Unable to connect to the camera. Please check your connection."
            );

        } finally {

            isUpdating = false;

        }
    }

    // Handle camera stream errors
    if (cameraFeed) {

        cameraFeed.addEventListener("error", () => {

            if (cameraError) {
                cameraError.textContent =
                    "Camera stream unavailable. Check webcam permissions and connection.";

                cameraError.style.display = "block";
            }

            if (cameraStatus) {
                cameraStatus.textContent = "Stream unavailable";
            }

            if (statusDot) {
                statusDot.classList.add("offline");
            }

        });

        cameraFeed.addEventListener("load", () => {

            if (cameraError) {
                cameraError.style.display = "none";
            }

        });
    }

    // Initial dashboard update
    updateDashboard();

    // Refresh dashboard statistics every second
    setInterval(updateDashboard, 1000);

});
