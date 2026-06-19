from flask import Flask, render_template, Response, jsonify,request
import cv2
import mediapipe as mp
import time
import sqlite3

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("gestures.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gestures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gesture TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
def clear_history():
    conn = sqlite3.connect("gestures.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM gestures")

    conn.commit()
    conn.close()

init_db()
clear_history()

def save_gesture(gesture):
    print("Saved:",gesture)
    conn = sqlite3.connect("gestures.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO gestures (gesture) VALUES (?)",
        (gesture,)
    )

    conn.commit()
    conn.close()
camera = None
camera_running = False


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7
)

last_spoken = ""
last_time = 0
current_gesture = "Waiting..."

def generate_frames():
    global last_spoken, last_time
    global current_gesture
    global camera
    global camera_running

    while camera_running:

        success, img = camera.read()

        if not success:
            break

        img = cv2.flip(img, 1)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        gesture = ""

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                lm = hand_landmarks.landmark

                fingers = []

                if lm[4].x < lm[3].x:
                    fingers.append(1)
                else:
                    fingers.append(0)

                tips = [8, 12, 16, 20]

                for tip in tips:
                    if lm[tip].y < lm[tip - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                if fingers == [0,0,0,0,0]:
                    gesture = "STOP"

                elif fingers == [0,1,0,0,0]:
                    gesture = "HELLO"

                elif fingers == [0,1,1,0,0]:
                    gesture = "THANK YOU"

                elif fingers == [0,1,1,1,0]:
                    gesture = "YES"

                elif fingers == [0,1,1,1,1]:
                    gesture = "NO"

                elif fingers == [1,0,0,0,0]:
                    gesture = "HELP"

                elif fingers == [1,1,0,0,1]:
                    gesture = "I LOVE YOU"

                elif fingers == [1,1,1,0,0]:
                    gesture = "PLEASE"

                elif fingers == [1,1,1,1,0]:
                    gesture = "SORRY"

                elif fingers == [1,1,1,1,1]:
                    gesture = "EAT"

                elif fingers == [0,0,1,0,0]:
                    gesture = "FRIEND"

                elif fingers == [0,0,0,0,1]:
                    gesture = "WATER"

                elif fingers == [0,0,0,1,0]:
                    gesture = "CALL"

                elif fingers == [0,0,0,1,1]:
                    gesture = "EMERGENCY"

                elif fingers == [0,0,1,0,1]:
                    gesture = "GOOD"

                elif fingers == [0,0,1,1,0]:
                    gesture = "FAMILY"

                elif fingers == [0,0,1,1,1]:
                    gesture = "HOME"

                elif fingers == [0,1,0,0,1]:
                    gesture = "DRINK"

                elif fingers == [0,1,0,1,0]:
                    gesture = "WELCOME"

                elif fingers == [0,1,0,1,1]:
                    gesture = "HOSPITAL"

                elif fingers == [0,1,1,0,1]:
                    gesture = "FOOD"

                elif fingers == [1,0,0,0,1]:
                    gesture = "BOOK"

                elif fingers == [1,0,0,1,0]:
                    gesture = "WORK"

                elif fingers == [1,0,0,1,1]:
                    gesture = "HUNGRY"

                elif fingers == [1,0,1,0,0]:
                    gesture = "STUDY"

                elif fingers == [1,0,1,0,1]:
                    gesture = "SCHOOL"

                elif fingers == [1,0,1,1,0]:
                    gesture = "COLLEGE"

                elif fingers == [1,0,1,1,1]:
                    gesture = "TEACHER"

                elif fingers == [1,1,0,0,0]:
                    gesture = "READY"

                elif fingers == [1,1,0,1,0]:
                    gesture = "QUESTION"

                elif fingers == [1,1,0,1,1]:
                    gesture = "GOODBYE"

                elif fingers == [1,1,1,0,1]:
                    gesture = "THANKS"

                else:
                    gesture = "UNKNOWN"

                current_gesture = gesture

                cv2.putText(
                    img,
                    gesture,
                    (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 255, 0),
                    3
                )

                if gesture != last_spoken and time.time() - last_time > 2:
                    #speaker.Speak(gesture)
                    save_gesture(gesture)
                    last_spoken = gesture
                    last_time = time.time()

        ret, buffer = cv2.imencode('.jpg', img)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/recognition')
def recognition():

    global camera
    global camera_running

    if not camera_running:
        camera = cv2.VideoCapture(0)
        camera_running = True

    return render_template('index.html')



@app.route('/start_camera')
def start_camera():

    global camera
    global camera_running

    if not camera_running:

        camera = cv2.VideoCapture(0)
        camera_running = True

    return jsonify({"status": "started"})


@app.route('/stop_camera')
def stop_camera():

    global camera
    global camera_running

    camera_running = False

    if camera is not None:
        camera.release()
        camera = None

    return jsonify({"status": "stopped"})


@app.route('/video')
def video():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
@app.route('/front_camera')
def front_camera():

    global camera
    global camera_running

    if camera is not None:
        camera.release()

    camera = cv2.VideoCapture(0)
    camera_running = True

    return jsonify({"status": "front"})


@app.route('/back_camera')
def back_camera():

    global camera
    global camera_running

    if camera is not None:
        camera.release()

    camera = cv2.VideoCapture(1)
    camera_running = True

    return jsonify({"status": "back"})

@app.route('/emergency_alert')
def emergency_alert():

    #speaker.Speak("Emergency! Please help me. I need assistance.")

    return jsonify({
        "message": "Emergency Alert Sent!"
    })
@app.route('/history')
def history():

    conn = sqlite3.connect("gestures.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM gestures ORDER BY id DESC LIMIT 20"
    )

    data = cursor.fetchall()

    conn.close()

    return jsonify(data)
@app.route('/gesture')
def gesture():
    return jsonify({"gesture": current_gesture})
if __name__ == "__main__":
    app.run(debug=True)