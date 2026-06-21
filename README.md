```markdown
# 🚗 Driver Drowsiness Detection System

> Real-time driver fatigue monitoring using MediaPipe Face Mesh,
> EAR/MAR analysis, and multi-level alert escalation.

## Motivation
Driver drowsiness causes over 20% of road accidents globally.
Traditional alert systems rely on steering behavior or expensive
hardware sensors. This project demonstrates a software-only,
camera-based approach using facial landmark analysis to detect
fatigue in real-time — deployable on any device with a webcam.

## Architecture
```
Webcam Feed
      ↓
MediaPipe Face Mesh (468 landmarks)
      ↓
EAR Computation (6 eye landmarks)
MAR Computation (6 mouth landmarks)
      ↓
Threshold Analysis + Frame Counter
      ↓
Multi-level Alert (WARNING→CRITICAL→EMERGENCY)
      ↓
Flask REST API + SQLite Logging
      ↓
React Live Dashboard (EAR/MAR/FPS telemetry)
```

## How It Works

### Eye Aspect Ratio (EAR)
EAR measures eye openness using 6 facial landmarks.
When EAR drops below threshold (0.25) for consecutive
frames, drowsiness is detected.

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
```

### Mouth Aspect Ratio (MAR)
MAR measures mouth openness using 6 landmarks.
High MAR sustained over frames indicates yawning.

### Alert Levels
| Frames | Alert Level | Action          |
|--------|-------------|-----------------|
| 8+     | WARNING     | Visual alert    |
| 15+    | CRITICAL    | Audio beep      |
| 25+    | EMERGENCY   | Loud alarm      |

## Performance

| Metric              | Value        |
|---------------------|--------------|
| Detection FPS       | 14–15 FPS    |
| EAR Threshold       | 0.25         |
| MAR Threshold       | 0.75         |
| Warning Trigger     | 8 frames     |
| Critical Trigger    | 15 frames    |
| Emergency Trigger   | 25 frames    |

## Tech Stack
- **CV/AI:** MediaPipe Face Mesh, OpenCV, SciPy
- **Backend:** Flask, SQLite
- **Frontend:** React, Vite, TailwindCSS
- **Audio:** Windows winsound (OS-level alerts)

## Features
- Real-time EAR/MAR computation at 14–15 FPS
- Three-tier alert escalation with audio notification
- Live dashboard streaming EAR/MAR/FPS telemetry
- Timestamped alert event logging to SQLite
- Post-session fatigue analysis via alert history
- Color-coded video border (green→yellow→orange→red)

## Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `localhost:5173`

## Requirements
```
flask
flask-cors
opencv-python
mediapipe==0.10.35
scipy
numpy
```

## API Endpoints

| Endpoint       | Method | Description              |
|----------------|--------|--------------------------|
| /video_feed    | GET    | Live MJPEG stream        |
| /status        | GET    | Current EAR/MAR/FPS/level|
| /alerts        | GET    | Last 20 alert events     |

## Known Limitations
- Requires adequate lighting for accurate detection
- Performance may vary with glasses or face coverings
- Single face detection only
- Windows-only audio alerts (winsound)

## Future Work
- Head pose estimation for distraction detection
- Multi-driver support
- Mobile deployment via TensorFlow Lite
- Integration with vehicle CAN bus for speed-based alerts
- Deep learning-based approach (replace EAR with CNN)
- Edge deployment on Raspberry Pi / Jetson Nano

## References
- Soukupová & Čech (2016) — Real-Time Eye Blink Detection
  using Facial Landmarks
- MediaPipe Face Mesh — Google AI
