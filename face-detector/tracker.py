import cv2
import mediapipe as mp

# Face tracker

def run_face_tracker():
    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils

    # Open default webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # MediaPipe requires RGB, OpenCV uses BGR
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)

        is_looking_at_screen = False

        if results.multi_face_landmarks:
            is_looking_at_screen = True
            for face_landmarks in results.multi_face_landmarks:
                # Draw the mesh over the face for the demo visual
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style()
                )
                
                # To get advanced: Extract specific points like the nose tip
                # nose_x = face_landmarks.landmark[1].x
                # nose_y = face_landmarks.landmark[1].y

        # Display status on the frame
        status_text = "Focused" if is_looking_at_screen else "DISTRACTED!"
        color = (0, 255, 0) if is_looking_at_screen else (0, 0, 255)
        cv2.putText(image, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow('Hackathon Face Tracker', image)
        
        # Press 'ESC' to exit
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_tracker()