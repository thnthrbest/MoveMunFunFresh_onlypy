from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2

model = YOLO("yolov8m.pt")  # เปลี่ยนจาก n->m (ขนาดกลาง แม่นกว่า เร็วพอ)
tracker = DeepSort(
    max_age=50,              # เพิ่มจาก 30 -> 50 จำได้นานขึ้นเมื่อคนหายชั่วคราว
    n_init=3,                # ลดจาก 5 -> 3 ยืนยัน ID เร็วขึ้น
    nms_max_overlap=0.7,     # กรองกรอบที่ซ้อนทับกัน
    max_cosine_distance=0.3  # เพิ่มความเข้มงวดในการจับคู่ features
)

cap = cv2.VideoCapture(1)

# ตัวแปรจัดการ ID
MAX_PEOPLE = 1
active_ids = set()  # เก็บ ID ที่กำลังใช้งาน
available_ids = list(range(1, MAX_PEOPLE + 1))  # [1, 2, 3]
id_mapping = {}  # แมป DeepSORT track_id -> custom_id ของเรา

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        break

    results = model(frame)

    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        clss = r.boxes.cls.cpu().numpy()

        detections = []
        for box, conf, cls in zip(boxes, confs, clss):
            if int(cls) == 0 and conf > 0.5:  # เฉพาะคน
                detections.append(([box[0], box[1], box[2]-box[0], box[3]-box[1]], conf, 'person'))

        tracks = tracker.update_tracks(detections, frame=frame)
        
        # เก็บ track_id ที่ยังมีอยู่ในเฟรมนี้
        current_track_ids = set()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            current_track_ids.add(track_id)
            
            # ถ้ายังไม่มี custom_id สำหรับ track นี้
            if track_id not in id_mapping:
                # ตรวจสอบว่ายังมี ID ว่างไหม
                if available_ids:
                    custom_id = available_ids.pop(0)  # เอา ID ที่ว่างตัวแรก
                    id_mapping[track_id] = custom_id
                    active_ids.add(custom_id)
                else:
                    # ถ้า ID เต็มแล้ว ไม่แสดงคนนี้
                    continue
            
            custom_id = id_mapping[track_id]
            
            # วาดกรอบและแสดง custom_id
            x1, y1, x2, y2 = track.to_ltrb()
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'ID {custom_id}', (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # คืน ID ของคนที่หลุดจากเฟรม
        disappeared_tracks = set(id_mapping.keys()) - current_track_ids
        for disappeared_track_id in disappeared_tracks:
            custom_id = id_mapping[disappeared_track_id]
            available_ids.append(custom_id)  # คืน ID กลับไปใช้ใหม่
            available_ids.sort()  # เรียงเพื่อให้ใช้ ID เล็กที่สุดก่อน
            active_ids.discard(custom_id)
            del id_mapping[disappeared_track_id]

    # แสดงจำนวนคนปัจจุบัน
    cv2.putText(frame, f'People: {len(active_ids)}/{MAX_PEOPLE}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("YOLOv8 + DeepSORT (Limited ID)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()