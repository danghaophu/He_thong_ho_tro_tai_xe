import cv2
import dlib
import numpy as np
import torch
from datetime import datetime
from scipy.spatial import distance as dist

# Lưu lịch sử trạng thái
detection_history = []

# Khởi tạo mô hình
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    r"E:\do an tot nghiep\SafeDriveVision-master\SafeDriveVision-master\shape_predictor_81_face_landmarks (1).dat")

weights_path = r'E:\do an tot nghiep\SafeDriveVision-master\SafeDriveVision-master\yolov5.pt'
model = torch.hub.load(
    r"E:\do an tot nghiep\SafeDriveVision-master\SafeDriveVision-master\yolov5",
    'custom',
    path=weights_path,
    source='local',
    force_reload=True
)
device = torch.device('cpu')
model.to(device)

# ====== TÍNH TOÁN CÁC CHỈ SỐ ======

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2], mouth[10])
    B = dist.euclidean(mouth[4], mouth[8])
    C = dist.euclidean(mouth[0], mouth[6])
    return (A + B) / (2.0 * C)

def calculate_head_angle(eye_left, eye_right, nose_tip):
    eye_center = (eye_left + eye_right) / 2
    vector_nose = nose_tip - eye_center
    vector_horizontal = (eye_right - eye_left)
    vector_horizontal[1] = 0
    vector_nose_normalized = vector_nose / np.linalg.norm(vector_nose)
    vector_horizontal_normalized = vector_horizontal / np.linalg.norm(vector_horizontal)
    angle_rad = np.arccos(np.clip(np.dot(vector_nose_normalized, vector_horizontal_normalized), -1.0, 1.0))
    return np.degrees(angle_rad)

# ====== HÀM CHÍNH ======

def detect_drowsiness(img, language='vi'):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 0)

    # Kiểm tra dùng điện thoại
    results = model(img)
    detections = results.xyxy[0]
    for detection in detections:
        if int(detection[5]) == 67:  # class "cell phone"
            status = "phone"
            break
    else:
        status = "normal"

        for face in faces:
            landmarks = predictor(gray, face)
            points = np.array([(p.x, p.y) for p in landmarks.parts()])
            left_eye = points[36:42]
            right_eye = points[42:48]
            mouth = points[48:68]

            ear = eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye) / 2.0
            mar = mouth_aspect_ratio(mouth)

            if ear < 0.35:
                status = "eye"
                break

            if mar > 0.4:
                status = "reposer"
                break

            
            eye_left = points[36]
            eye_right = points[45]
            nose_tip = points[33]
            head_angle = calculate_head_angle(np.array(eye_left), np.array(eye_right), np.array(nose_tip))

            if head_angle < 75 or head_angle > 110:
                status = "regarder"
                break

        if len(faces) == 0:
            status = "regarder"

    # Lưu vào lịch sử nếu khác lần trước
    if len(detection_history) == 0 or detection_history[-1]['status'] != status:
        detection_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status
        })

    return status
