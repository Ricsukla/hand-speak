import cv2
import mediapipe as mp
import time
from collections import deque

# ============================================================
# MEDIAPIPE SETUP
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

# ============================================================
# COLORS
# ============================================================

BG = (18, 20, 28)
PANEL = (28, 31, 42)
PANEL_2 = (35, 38, 52)

WHITE = (245, 245, 245)
LIGHT = (180, 185, 200)
GREEN = (80, 220, 150)
CYAN = (80, 210, 255)
PURPLE = (170, 120, 255)
RED = (90, 90, 255)

# ============================================================
# GESTURES
# ============================================================

GESTURES = [
    "LIKE",
    "DISLIKE",
    "OK",
    "PEACE",
    "CALL ME",
    "STOP",
    "FORWARD",
    "LEFT",
    "RIGHT",
    "I LOVE YOU"
]

finger_tips = [8, 12, 16, 20]
thumb_tip = 4

current_gesture = "NO GESTURE"
history = deque(maxlen=5)

last_gesture = ""
last_detection_time = 0

# ============================================================
# FPS
# ============================================================

prev_time = 0


# ============================================================
# UI FUNCTIONS
# ============================================================

def rounded_box(img, x1, y1, x2, y2, color, radius=18):
    cv2.rectangle(
        img,
        (x1 + radius, y1),
        (x2 - radius, y2),
        color,
        -1
    )

    cv2.rectangle(
        img,
        (x1, y1 + radius),
        (x2, y2 - radius),
        color,
        -1
    )

    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)


def text(img, value, position, size=0.6, color=WHITE, thickness=1):
    cv2.putText(
        img,
        value,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA
    )


def add_detection(gesture):
    global last_gesture, last_detection_time

    now = time.time()

    # Avoid adding the same gesture every frame
    if gesture != last_gesture or now - last_detection_time > 1.5:
        history.appendleft(
            time.strftime("%H:%M:%S") + "   " + gesture
        )

        last_gesture = gesture
        last_detection_time = now


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame.")
        break

    frame = cv2.flip(frame, 1)

    # Resize camera
    frame = cv2.resize(frame, (960, 540))

    h, w, _ = frame.shape

    # FPS
    current_time = time.time()

    if prev_time != 0:
        fps = 1 / (current_time - prev_time)
    else:
        fps = 0

    prev_time = current_time

    # --------------------------------------------------------
    # MEDIAPIPE
    # --------------------------------------------------------

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    detected_gesture = "NO GESTURE"
    hand_count = 0

    # --------------------------------------------------------
    # GESTURE DETECTION
    # --------------------------------------------------------

    if results.multi_hand_landmarks:

        hand_count = len(results.multi_hand_landmarks)

        for hand_landmarks in results.multi_hand_landmarks:

            lm_list = []

            for lm in hand_landmarks.landmark:
                lm_list.append(lm)

            finger_fold_status = []

            for tip in finger_tips:

                if lm_list[tip].x < lm_list[tip - 3].x:
                    finger_fold_status.append(True)
                else:
                    finger_fold_status.append(False)

            # LIKE
            if (
                lm_list[thumb_tip].y <
                lm_list[thumb_tip - 1].y <
                lm_list[thumb_tip - 2].y
            ):
                if all(finger_fold_status):
                    detected_gesture = "LIKE"

            # DISLIKE
            if (
                lm_list[thumb_tip].y >
                lm_list[thumb_tip - 1].y >
                lm_list[thumb_tip - 2].y
            ):
                if all(finger_fold_status):
                    detected_gesture = "DISLIKE"

            # OK
            thumb_x = lm_list[thumb_tip].x
            thumb_y = lm_list[thumb_tip].y

            index_x = lm_list[8].x
            index_y = lm_list[8].y

            distance = (
                (thumb_x - index_x) ** 2 +
                (thumb_y - index_y) ** 2
            ) ** 0.5

            if distance < 0.05:
                if (
                    not finger_fold_status[1]
                    and not finger_fold_status[2]
                    and not finger_fold_status[3]
                ):
                    detected_gesture = "OK"

            # PEACE
            ring_x = lm_list[16].x
            ring_y = lm_list[16].y

            pinky_x = lm_list[20].x
            pinky_y = lm_list[20].y

            distance_thumb_ring = (
                (thumb_x - ring_x) ** 2 +
                (thumb_y - ring_y) ** 2
            ) ** 0.5

            distance_ring_pinky = (
                (ring_x - pinky_x) ** 2 +
                (ring_y - pinky_y) ** 2
            ) ** 0.5

            if (
                distance_thumb_ring < 0.05
                and distance_ring_pinky < 0.05
            ):
                if (
                    not finger_fold_status[0]
                    and not finger_fold_status[1]
                ):
                    detected_gesture = "PEACE"

            # CALL ME
            if (
                finger_fold_status[0]
                and finger_fold_status[1]
                and finger_fold_status[3]
            ):

                distance_thumb_pinky = (
                    (thumb_x - pinky_x) ** 2 +
                    (thumb_y - pinky_y) ** 2
                ) ** 0.5

                if distance_thumb_pinky > 0.4:
                    detected_gesture = "CALL ME"

            # STOP
            if (
                lm_list[thumb_tip].y <
                lm_list[thumb_tip - 1].y <
                lm_list[thumb_tip - 2].y
                and
                lm_list[8].y <
                lm_list[6].y <
                lm_list[5].y
                and
                lm_list[12].y <
                lm_list[10].y <
                lm_list[9].y
                and
                lm_list[16].y <
                lm_list[14].y <
                lm_list[13].y
                and
                lm_list[20].y <
                lm_list[18].y <
                lm_list[17].y
            ):
                detected_gesture = "STOP"

            # FORWARD
            if (
                lm_list[8].y <
                lm_list[6].y <
                lm_list[5].y
                and
                lm_list[12].y >
                lm_list[11].y >
                lm_list[10].y
                and
                lm_list[16].y >
                lm_list[15].y >
                lm_list[14].y
                and
                lm_list[20].y >
                lm_list[19].y >
                lm_list[18].y
                and
                lm_list[thumb_tip].x >
                lm_list[thumb_tip - 1].x
            ):
                detected_gesture = "FORWARD"

            # LEFT
            if (
                lm_list[4].y < lm_list[2].y
                and
                lm_list[8].x < lm_list[6].x
                and
                lm_list[12].x > lm_list[10].x
                and
                lm_list[16].x > lm_list[14].x
                and
                lm_list[20].x > lm_list[18].x
                and
                lm_list[5].x < lm_list[0].x
            ):
                detected_gesture = "LEFT"

            # RIGHT
            if (
                lm_list[4].y < lm_list[2].y
                and
                lm_list[8].x > lm_list[6].x
                and
                lm_list[12].x < lm_list[10].x
                and
                lm_list[16].x < lm_list[14].x
                and
                lm_list[20].x < lm_list[18].x
            ):
                detected_gesture = "RIGHT"

            # I LOVE YOU
            if (
                lm_list[8].y <
                lm_list[6].y <
                lm_list[5].y
                and
                lm_list[12].y >
                lm_list[11].y >
                lm_list[10].y
                and
                lm_list[16].y >
                lm_list[15].y >
                lm_list[14].y
                and
                lm_list[20].y <
                lm_list[19].y <
                lm_list[18].y
                and
                lm_list[thumb_tip].x >
                lm_list[thumb_tip - 1].x
            ):
                detected_gesture = "I LOVE YOU"

            # Draw landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

    current_gesture = detected_gesture

    if detected_gesture != "NO GESTURE":
        add_detection(detected_gesture)

    # ========================================================
    # CREATE DASHBOARD
    # ========================================================

    dashboard_width = 1380
    dashboard_height = 760

    canvas = cv2.resize(
        frame,
        (960, 540)
    )

    dashboard = cv2.imread(
        "/dev/null"
    ) if False else None

    dashboard = __import__("numpy").zeros(
        (dashboard_height, dashboard_width, 3),
        dtype="uint8"
    )

    dashboard[:] = BG

    # ========================================================
    # HEADER
    # ========================================================

    text(
        dashboard,
        "SIGNVISION",
        (45, 55),
        1.1,
        WHITE,
        2
    )

    text(
        dashboard,
        "REAL-TIME HAND GESTURE RECOGNITION",
        (45, 85),
        0.45,
        LIGHT
    )

    # Camera status
    cv2.circle(
        dashboard,
        (1210, 48),
        7,
        GREEN,
        -1
    )

    text(
        dashboard,
        "CAMERA ACTIVE",
        (1230, 54),
        0.45,
        GREEN,
        1
    )

    # Header line
    cv2.line(
        dashboard,
        (35, 110),
        (1345, 110),
        (55, 58, 75),
        1
    )

    # ========================================================
    # CAMERA PANEL
    # ========================================================

    rounded_box(
        dashboard,
        35, 135,
        980, 650,
        PANEL,
        20
    )

    # Camera image
    camera = cv2.resize(canvas, (920, 518))

    dashboard[
        155:673,
        55:975
    ] = camera

    # Camera label
    text(
        dashboard,
        "LIVE CAMERA",
        (70, 150),
        0.45,
        CYAN,
        1
    )

    # ========================================================
    # RIGHT PANEL
    # ========================================================

    rounded_box(
        dashboard,
        1035, 135,
        1345, 330,
        PANEL,
        20
    )

    text(
        dashboard,
        "CURRENT GESTURE",
        (1060, 170),
        0.45,
        LIGHT
    )

    # Gesture
    gesture_display = current_gesture

    gesture_size = 0.9

    if gesture_display == "NO GESTURE":
        gesture_color = LIGHT
    else:
        gesture_color = GREEN

    text(
        dashboard,
        gesture_display,
        (1060, 220),
        gesture_size,
        gesture_color,
        2
    )

    # Detection status
    cv2.circle(
        dashboard,
        (1065, 265),
        6,
        GREEN if hand_count else RED,
        -1
    )

    text(
        dashboard,
        "HAND DETECTED" if hand_count else "NO HAND",
        (1080, 270),
        0.5,
        WHITE
    )

    # FPS
    text(
        dashboard,
        f"FPS     {fps:.1f}",
        (1060, 310),
        0.45,
        LIGHT
    )

    text(
        dashboard,
        f"HANDS   {hand_count}",
        (1190, 310),
        0.45,
        LIGHT
    )

    # ========================================================
    # HISTORY PANEL
    # ========================================================

    rounded_box(
        dashboard,
        1035, 350,
        1345, 650,
        PANEL,
        20
    )

    text(
        dashboard,
        "DETECTION HISTORY",
        (1060, 385),
        0.45,
        LIGHT
    )

    y = 425

    if len(history) == 0:

        text(
            dashboard,
            "Waiting for gesture...",
            (1060, y),
            0.45,
            LIGHT
        )

    else:

        for item in history:

            text(
                dashboard,
                item,
                (1060, y),
                0.43,
                WHITE
            )

            y += 42

    # ========================================================
    # SUPPORTED GESTURES
    # ========================================================

    text(
        dashboard,
        "SUPPORTED",
        (65, 710),
        0.4,
        LIGHT
    )

    supported_text = (
        "LIKE   DISLIKE   OK   PEACE   CALL ME   STOP   "
        "FORWARD   LEFT   RIGHT   I LOVE YOU"
    )

    text(
        dashboard,
        supported_text,
        (65, 735),
        0.38,
        WHITE
    )

    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        "SIGNVISION - Hand Gesture Recognition",
        dashboard
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()
hands.close()

print("SIGNVISION closed successfully.")