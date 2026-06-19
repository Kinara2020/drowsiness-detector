from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import json

from matplotlib.pylab import get_state
from detector import process_frame
from database import init_db, log_alert, get_alerts
import winsound

app = Flask(__name__)
CORS(app)
init_db()

cap = cv2.VideoCapture(0)
last_alert = {"drowsy": False, "yawning": False}

def generate_frames():
    global last_alert
    while True:
        success, frame = cap.read()
        if not success:
            break

        state = process_frame(frame)

        # Log new alerts (debounced)
        if state["drowsy"] and not last_alert["drowsy"]:
            log_alert("DROWSY", state["ear"], state["mar"])
        if state["yawning"] and not last_alert["yawning"]:
            log_alert("YAWN", state["ear"], state["mar"])
        last_alert = {"drowsy": state["drowsy"], "yawning": state["yawning"]}

        # Draw overlay
        level = state["alert_level"]
        color = {
              "OK": (0, 255, 0),
              "WARNING": (0, 165, 255),
              "CRITICAL": (0, 0, 255),
              "EMERGENCY": (0, 0, 180)
          }.get(level, (255, 255, 255))

        cv2.putText(frame, f"{level}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"EAR: {state['ear']}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"MAR: {state['mar']}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, f"FPS: {state['fps']}", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    recent = get_alerts(1)
    state = get_state.copy()
    return jsonify({
        "alert_level": state.get("alert_level", "OK"),
        "ear": state.get("ear", 1.0),
        "mar": state.get("mar", 0.0),
        "fps": state.get("fps", 0)
    })

@app.route('/alerts')
def alerts():
    return jsonify(get_alerts(20))

if __name__ == '__main__':
    app.run(debug=True, port=5000)