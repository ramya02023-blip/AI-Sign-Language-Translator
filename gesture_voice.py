import cv2
import mediapipe as mp
import win32com.client
import time

speaker = win32com.client.Dispatch("SAPI.SpVoice")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)

last_spoken = ""
last_time = 0

while True:
    success, img = cap.read()

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

            # Thumb
            if lm[4].x < lm[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

            # Other fingers
            tips = [8, 12, 16, 20]

            for tip in tips:
                if lm[tip].y < lm[tip - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total = fingers.count(1)
            total = fingers.count(1)
            total = fingers.count(1)

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

            else:
              gesture = "UNKNOWN"
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
                print("Speaking:", gesture)
                speaker.Speak(gesture)
                last_spoken = gesture
                last_time = time.time()

    cv2.imshow("Gesture Voice", img)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()