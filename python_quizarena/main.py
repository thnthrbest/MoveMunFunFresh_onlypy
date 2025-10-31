"""
Python Server สำหรับ Unity Integration
- รับภาพจาก Unity
- รับค่าจำนวนคนสูงสุดจาก Unity
- ประมวลผลด้วย YOLO + DeepSORT
- ส่งภาพที่ประมวลผลแล้วและข้อมูลกลับไป Unity
"""

from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
import socket
import struct
import json
import threading
import time

# ==================== Configuration ====================
HOST = '0.0.0.0'  # รับจากทุก IP
PORT = 5555       # Port สำหรับรับภาพจาก Unity
DATA_PORT = 5556  # Port สำหรับส่งข้อมูลกลับ Unity

# ==================== Load Model ====================
print(" Loading YOLO model...")
model = YOLO("yolov8n.pt")
model.fuse()

try:
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cuda':
        model.to('cuda')
    print(f" Using device: {device}")
except:
    device = 'cpu'
    print(" Using CPU")

# ==================== DeepSORT ====================
tracker = DeepSort(
    max_age=70,
    n_init=2,
    nms_max_overlap=0.8,
    max_cosine_distance=0.4,
    nn_budget=100,
    max_iou_distance=0.7
)

# ==================== Global Variables ====================
MAX_PEOPLE = 3  # Default, จะอัพเดตจาก Unity
active_ids = set()
available_ids = list(range(1, MAX_PEOPLE + 1))
id_mapping = {}
smoothed_positions = {}
velocity_tracking = {}
last_seen = {}

MOTION_SMOOTHING = 0.5
VELOCITY_WEIGHT = 0.5
CONF_THRESHOLD = 0.45

latest_frame = None
processed_frame = None
frame_lock = threading.Lock()
running = True

# ==================== Helper Functions ====================
def update_max_people(new_max):
    """อัพเดตจำนวนคนสูงสุด"""
    global MAX_PEOPLE, available_ids
    MAX_PEOPLE = new_max
    # รีเซ็ต IDs ที่ยังไม่ได้ใช้
    used_ids = set(id_mapping.values())
    available_ids = [i for i in range(1, MAX_PEOPLE + 1) if i not in used_ids]
    available_ids.sort()
    print(f" Max people updated to: {MAX_PEOPLE}")

def reset_tracking():
    """รีเซ็ตระบบติดตาม"""
    global active_ids, available_ids, id_mapping, smoothed_positions, velocity_tracking, last_seen
    active_ids.clear()
    available_ids = list(range(1, MAX_PEOPLE + 1))
    id_mapping.clear()
    smoothed_positions.clear()
    velocity_tracking.clear()
    last_seen.clear()
    print(" Tracking system reset")

def get_tracking_data():
    """สร้างข้อมูลสำหรับส่งไป Unity"""
    data = {
        'current_people': len(active_ids),
        'max_people': MAX_PEOPLE,
        'people': []
    }
    
    for custom_id in active_ids:
        if custom_id in smoothed_positions:
            x1, y1, x2, y2 = smoothed_positions[custom_id]
            vx, vy = velocity_tracking.get(custom_id, (0, 0))
            speed = np.sqrt(vx**2 + vy**2)
            
            person_data = {
                'id': int(custom_id),
                'x': float((x1 + x2) / 2),  # Center X
                'y': float((y1 + y2) / 2),  # Center Y
                'width': float(x2 - x1),
                'height': float(y2 - y1),
                'speed': float(speed),
                'velocity_x': float(vx),
                'velocity_y': float(vy)
            }
            data['people'].append(person_data)
    
    return data

# ==================== Image Receiver Thread ====================
def receive_from_unity():
    """รับภาพจาก Unity"""
    global latest_frame, running, MAX_PEOPLE
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    
    print(f" Waiting for Unity connection on {HOST}:{PORT}...")
    
    conn, addr = server.accept()
    print(f" Unity connected from {addr}")
    
    data = b""
    payload_size = struct.calcsize("Q")
    
    while running:
        try:
            # รับขนาดของ packet
            while len(data) < payload_size:
                packet = conn.recv(4096)
                if not packet:
                    raise ConnectionError("Connection lost")
                data += packet
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            
            # รับข้อมูลภาพ
            while len(data) < msg_size:
                packet = conn.recv(4096)
                if not packet:
                    raise ConnectionError("Connection lost")
                data += packet
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # แปลง bytes เป็นภาพ
            frame_array = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is not None:
                with frame_lock:
                    latest_frame = frame
            
        except Exception as e:
            print(f" Connection error: {e}")
            break
    
    conn.close()
    server.close()

# ==================== Data Sender Thread ====================
def send_to_unity():
    """ส่งภาพที่ประมวลแล้วและข้อมูลกลับไป Unity"""
    global processed_frame, running
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, DATA_PORT))
    server.listen(1)
    
    print(f" Waiting for Unity data connection on {HOST}:{DATA_PORT}...")
    
    conn, addr = server.accept()
    print(f" Unity data connected from {addr}")
    
    while running:
        try:
            if processed_frame is not None:
                with frame_lock:
                    frame_to_send = processed_frame.copy()
                
                # เข้ารหัสภาพ
                _, buffer = cv2.imencode('.jpg', frame_to_send, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()
                
                # สร้าง JSON data
                tracking_data = get_tracking_data()
                json_data = json.dumps(tracking_data).encode('utf-8')
                
                # ส่งข้อมูล: [image_size][image][json_size][json]
                message = struct.pack("Q", len(frame_bytes)) + frame_bytes
                message += struct.pack("Q", len(json_data)) + json_data
                
                conn.sendall(message)
            
            time.sleep(0.03)  # ~30 FPS
            
        except Exception as e:
            print(f"❌ Send error: {e}")
            break
    
    conn.close()
    server.close()

# ==================== Command Receiver Thread ====================
def receive_commands():
    """รับคำสั่งจาก Unity (เช่น เปลี่ยนจำนวนคนสูงสุด)"""
    global running, MAX_PEOPLE
    
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT + 2))  # Port 5557
    
    print(f"  Command receiver ready on port {PORT + 2}")
    
    while running:
        try:
            data, addr = server.recvfrom(1024)
            command = json.loads(data.decode('utf-8'))
            
            if 'max_people' in command:
                update_max_people(command['max_people'])
            
            if command.get('reset', False):
                reset_tracking()
            
        except Exception as e:
            print(f"⚠️  Command error: {e}")
            time.sleep(0.1)
    
    server.close()

# ==================== Processing Thread ====================
def process_frames():
    """ประมวลผลภาพด้วย YOLO + DeepSORT"""
    global latest_frame, processed_frame, running
    global active_ids, available_ids, id_mapping
    global smoothed_positions, velocity_tracking, last_seen
    
    frame_count = 0
    fps_start = time.time()
    fps_count = 0
    current_fps = 0
    
    print(" Processing started...")
    
    while running:
        if latest_frame is None:
            time.sleep(0.01)
            continue
        
        with frame_lock:
            frame = latest_frame.copy()
        
        frame_count += 1
        fps_count += 1
        
        # คำนวณ FPS
        if fps_count >= 30:
            current_fps = fps_count / (time.time() - fps_start)
            fps_start = time.time()
            fps_count = 0
        
        # ปรับภาพ
        frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=5)
        
        # YOLO Detection
        results = model.predict(
            frame,
            conf=CONF_THRESHOLD,
            iou=0.3,
            imgsz=640,
            half=(device == 'cuda'),
            device=device,
            verbose=False,
            classes=[0]
        )
        
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            clss = r.boxes.cls.cpu().numpy()
            
            detections = []
            for box, conf, cls in zip(boxes, confs, clss):
                if int(cls) == 0:
                    detections.append(([box[0], box[1], box[2]-box[0], box[3]-box[1]], conf, 'person'))
            
            tracks = tracker.update_tracks(detections, frame=frame)
            
            current_track_ids = set()
            current_time = time.time()
            
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                current_track_ids.add(track_id)
                
                if track_id not in id_mapping:
                    if available_ids:
                        custom_id = available_ids.pop(0)
                        id_mapping[track_id] = custom_id
                        active_ids.add(custom_id)
                        print(f" Person ID {custom_id} detected")
                    else:
                        continue
                
                custom_id = id_mapping[track_id]
                last_seen[custom_id] = current_time
                
                # Velocity prediction
                x1, y1, x2, y2 = track.to_ltrb()
                
                if custom_id in smoothed_positions:
                    prev_x1, prev_y1, prev_x2, prev_y2 = smoothed_positions[custom_id]
                    
                    vx = (x1 - prev_x1)
                    vy = (y1 - prev_y1)
                    
                    if custom_id in velocity_tracking:
                        prev_vx, prev_vy = velocity_tracking[custom_id]
                        vx = 0.7 * prev_vx + 0.3 * vx
                        vy = 0.7 * prev_vy + 0.3 * vy
                    
                    velocity_tracking[custom_id] = (vx, vy)
                    
                    predicted_x1 = x1 + vx * VELOCITY_WEIGHT
                    predicted_y1 = y1 + vy * VELOCITY_WEIGHT
                    predicted_x2 = x2 + vx * VELOCITY_WEIGHT
                    predicted_y2 = y2 + vy * VELOCITY_WEIGHT
                    
                    x1 = MOTION_SMOOTHING * prev_x1 + (1 - MOTION_SMOOTHING) * predicted_x1
                    y1 = MOTION_SMOOTHING * prev_y1 + (1 - MOTION_SMOOTHING) * predicted_y1
                    x2 = MOTION_SMOOTHING * prev_x2 + (1 - MOTION_SMOOTHING) * predicted_x2
                    y2 = MOTION_SMOOTHING * prev_y2 + (1 - MOTION_SMOOTHING) * predicted_y2
                else:
                    velocity_tracking[custom_id] = (0, 0)
                
                smoothed_positions[custom_id] = (x1, y1, x2, y2)
                
                # วาดกรอบ
                speed = np.sqrt(velocity_tracking[custom_id][0]**2 + velocity_tracking[custom_id][1]**2)
                if speed > 10:
                    color = (0, 0, 255)
                    status = "FAST"
                elif speed > 5:
                    color = (0, 165, 255)
                    status = "MEDIUM"
                else:
                    color = (0, 255, 0)
                    status = "SLOW"
                
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f'ID {custom_id}', (int(x1), int(y1)-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f'{status}', (int(x1), int(y2)+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # ลบคนที่หายไป
            disappeared_tracks = set(id_mapping.keys()) - current_track_ids
            for disappeared_track_id in disappeared_tracks:
                custom_id = id_mapping[disappeared_track_id]
                
                if custom_id in last_seen and (current_time - last_seen[custom_id]) > 2.0:
                    available_ids.append(custom_id)
                    available_ids.sort()
                    active_ids.discard(custom_id)
                    del id_mapping[disappeared_track_id]
                    if custom_id in smoothed_positions:
                        del smoothed_positions[custom_id]
                    if custom_id in velocity_tracking:
                        del velocity_tracking[custom_id]
                    if custom_id in last_seen:
                        del last_seen[custom_id]
                    print(f" Person ID {custom_id} left")
        
        # วาดข้อมูล
        cv2.putText(frame, f'People: {len(active_ids)}/{MAX_PEOPLE}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f'FPS: {current_fps:.1f}', (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.circle(frame, (frame.shape[1] - 20, 20), 8, (0, 255, 0), -1)
        cv2.putText(frame, 'CONNECTED', (frame.shape[1] - 120, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        with frame_lock:
            processed_frame = frame
        
        # แสดงหน้าต่างสำหรับ debug (ถ้าต้องการ)
        cv2.imshow("Processing", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            running = False

# ==================== Main ====================
if __name__ == "__main__":
    print("=" * 60)
    print(" UNITY INTEGRATION SERVER")
    print("=" * 60)
    print(f" Image receiver port: {PORT}")
    print(f" Data sender port: {DATA_PORT}")
    print(f"  Command port: {PORT + 2}")
    print(f" Default max people: {MAX_PEOPLE}")
    print("=" * 60)
    
    # Start threads
    receiver_thread = threading.Thread(target=receive_from_unity, daemon=True)
    sender_thread = threading.Thread(target=send_to_unity, daemon=True)
    command_thread = threading.Thread(target=receive_commands, daemon=True)
    processor_thread = threading.Thread(target=process_frames, daemon=True)
    
    receiver_thread.start()
    sender_thread.start()
    command_thread.start()
    processor_thread.start()
    
    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        running = False
    
    cv2.destroyAllWindows()
    print(" Server closed")