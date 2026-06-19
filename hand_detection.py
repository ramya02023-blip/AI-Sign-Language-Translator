import cv2
import mediapipe as mp

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()

    if not success:
        print("Failed to access camera")
        break

    # Flip image for natural view
    img = cv2.flip(img, 1)

    # Convert BGR to RGB
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process frame
    results = hands.process(rgb)

    # Detect hands
    if results.multi_hand_landmarks:

        cv2.putText(
            img,
            "Hand Detected",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Print landmark coordinates
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

    else:
        cv2.putText(
            img,
            "No Hand Detected",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv2.imshow("Hand Detection", img)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()