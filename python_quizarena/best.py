from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
import socket
import struct
import json
import threading
import time

print(" Loading YOLO model...")
model = YOLO("yolov8n.pt")
model.fuse()

tracker = DeepSort(
    max_age=70,
    n_init=2,
    nms_max_overlap=0.8,
    max_cosine_distance=0.4,
    nn_budget=100,
    max_iou_distance=0.7
)

#<---- Setting Socket---->

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockImg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddressPort = ("127.0.0.1", 6052) # Send y

#<---- Setting Socket---->

# ==================== Global Variables ====================

NowRun = True 
MAX_PEOPLE = 3
active_ids = set()  # เก็บ ID ที่กำลังใช้งาน
available_ids = list(range(1, MAX_PEOPLE + 1))  # [1, 2, 3]
id_mapping = {}  # แมป DeepSORT track_id -> custom_id ของเรา
# ==================== Global Variables ====================

#<---- function num people : Thread---->

# def ReciveValue():
#     global MAX_PEOPLE,active_ids,available_ids,id_mapping

#<---- function num people : Thread end---->

#<---- Receive img ---->
def procressimg():
    global client_socket
    sockImg.bind(("127.0.0.1", 6055))
    sockImg.listen(1)
    print("Waiting for connection...")
    client_socket, client_address = sockImg.accept()
    print(f"Connected to {client_address}")
    # unity_recive_state_thread = threading.Thread(target=ReciveValue)
    # unity_recive_state_thread.start()

    while True:

        # Receive the length of the incoming frame
        length_data = client_socket.recv(4)
        if not length_data:
            break
        length = struct.unpack('I', length_data)[0]

        # Receive the image data from Unity
        image_data = b""
        while len(image_data) < length:
            image_data += client_socket.recv(length - len(image_data))

        # Convert the image data to a NumPy array and decode it
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
        frame = img

        frame = cv2.flip(frame, 1)

        results = model(frame, verbose=False)

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

                # จุดตรงกลางของกรอบด้านบน
                center_top_x = int((x1 + x2) / 2)
                center_top_y = int(y1+50)
                cv2.circle(frame, (center_top_x, center_top_y), 5, (0, 0, 255), -1)  # จุดสีแดง

                sock.sendto(str.encode(f"{custom_id}:{center_top_x}"), serverAddressPort)

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

            # Send Process Image To Unity 
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()

        # Send the length of the processed frame and the frame itself
        client_socket.send(struct.pack('I', len(frame_bytes)))
        client_socket.send(frame_bytes)

#<---- Receive img end ---->

sock_unity_revice = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_unity_revice.bind(("127.0.0.1", 6051)) # Recive Value form unity (start anything)
print(f"Listening on Unity : ReciveValue NUM.... ")
data, addr = sock_unity_revice.recvfrom(1024)
data = data.decode('utf-8')
MAX_PEOPLE = int(data)
active_ids = set()  # เก็บ ID ที่กำลังใช้งาน
available_ids = list(range(1, MAX_PEOPLE + 1))  # [1, 2, 3]
id_mapping = {}  # แมป DeepSORT track_id -> custom_id ของเรา
if(data != ""):
    print(f"Recive NUM People : {data}")
    procressimg()

#<---- Clean up ---->

NowRun = False
print("clean")
client_socket.close()
sockImg.close()
cv2.destroyAllWindows()

#<---- Clean up ---->