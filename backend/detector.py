import cv2
import numpy as np
from scipy.spatial import distance
import mediapipe as mp
import threading
import winsound

mp_face_mesh = mp.tasks.vision.FaceLandmarkerOptions
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
MOUTH     = [13,  312, 87,  178, 324, 82]

EAR_THRESHOLD     = 0.25
MOUTH_THRESHOLD   = 0.75
EAR_WARNING       = 8   # frames → WARNING
EAR_CRITICAL      = 15  # frames → CRITICAL
EAR_EMERGENCY     = 50   # frames → EMERGENCY

frame_counter = 0
yawn_counter  = 0
alert_playing = False
alert_state   = {
    "drowsy": False, "yawning": False,
    "ear": 1.0, "mar": 0.0,
    "alert_level": "OK", "fps": 0
}

options = mp.tasks.vision.FaceLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=mp.tasks.vision.RunningMode.IMAGE,
    num_faces=1
)
detector = mp.tasks.vision.FaceLandmarker.create_from_options(options)

import time
prev_time = time.time()

def play_alert():
    global alert_playing
    if not alert_playing:
        alert_playing = True
        threading.Thread(target=_play, daemon=True).start()

def _play():
    global alert_playing
    winsound.Beep(880, 500)  
    alert_playing = False

def ear_ratio(lm, idx, w, h):
    pts = [(lm[i].x * w, lm[i].y * h) for i in idx]
    A = distance.euclidean(pts[1], pts[5])
    B = distance.euclidean(pts[2], pts[4])
    C = distance.euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C)

def process_frame(frame):
    global frame_counter, yawn_counter, alert_state, prev_time

    h, w = frame.shape[:2]

    # FPS
    now = time.time()
    fps = int(1 / (now - prev_time + 1e-9))
    prev_time = now

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    alert_state = {
        "drowsy": False, "yawning": False,
        "ear": 1.0, "mar": 0.0,
        "alert_level": "OK", "fps": fps
    }

    if result.face_landmarks:
        lm = result.face_landmarks[0]
        e = (ear_ratio(lm, LEFT_EYE, w, h) + ear_ratio(lm, RIGHT_EYE, w, h)) / 2.0
        m = ear_ratio(lm, MOUTH, w, h)

        alert_state["ear"] = round(e, 3)
        alert_state["mar"] = round(m, 3)

        # Multi-level drowsiness
        if e < EAR_THRESHOLD:
            frame_counter += 1
            if frame_counter >= EAR_EMERGENCY:
                alert_state["alert_level"] = "EMERGENCY"
                alert_state["drowsy"] = True
                play_alert()
            elif frame_counter >= EAR_CRITICAL:
                alert_state["alert_level"] = "CRITICAL"
                alert_state["drowsy"] = True
                play_alert()
            elif frame_counter >= EAR_WARNING:
                alert_state["alert_level"] = "WARNING"
                alert_state["drowsy"] = True
        else:
            frame_counter = 0

        # Yawn
        if m > MOUTH_THRESHOLD:
            yawn_counter += 1
            if yawn_counter > 15:
                alert_state["yawning"] = True
                play_alert()
                alert_state["alert_level"] = "WARNING" if alert_state["alert_level"] == "OK" else alert_state["alert_level"]
        else:
            yawn_counter = 0

    return alert_state