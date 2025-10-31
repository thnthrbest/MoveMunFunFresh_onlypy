import socket
import cv2
import mediapipe as mp
import numpy as np
import struct  
import json    

HOST = '127.0.0.1'
PORT = 7052 

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils # (เวอร์ชันช้า ต้องมี)
pose = mp_pose.Pose(
    static_image_mode=False, 
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet: return None
            data.extend(packet)
        except Exception:
            return None
    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"เซิร์ฟเวอร์กำลังรอการเชื่อมต่อที่ {HOST}:{PORT} ...")

    conn, addr = s.accept()
    with conn:
        print(f"เชื่อมต่อแล้วจาก {addr}")
        
        while True:
            try:
                # 1. รับภาพจาก Unity
                img_len_data = recvall(conn, 4)
                if not img_len_data: break
                img_len = struct.unpack('<I', img_len_data)[0]
                img_data = recvall(conn, img_len)
                if not img_data: break

                # 2. ประมวลผล
                img_np = np.frombuffer(img_data, dtype=np.uint8)
                frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                # --- ⭐️ 1. เพิ่มโค้ดกัน Crash (ถ้าภาพพัง) ---
                if frame is None:
                    print("ได้รับเฟรมภาพที่ไม่ถูกต้องจาก Unity... ข้ามเฟรมนี้")
                    continue # <-- ข้ามไปรอเฟรมถัดไป (ไม่ Crash)
                # --- ------------------------------------ ---

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)

                # 3. (ส่วนส่งภาพกลับ - เวอร์ชันช้า)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                success, processed_img_bytes = cv2.imencode('.jpg', frame)
                
                len_data_out = struct.pack('<I', len(processed_img_bytes))
                conn.sendall(len_data_out)
                conn.sendall(processed_img_bytes)

                # 4. ส่ง JSON (เหมือนเดิม)
                LANDMARKS_TO_SEND = [
                    0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 31, 32
                ]
                landmarks_list = []
                if results.pose_landmarks:
                    for i in LANDMARKS_TO_SEND:
                        lm = results.pose_landmarks.landmark[i]
                        landmarks_list.append({
                            "id": i, "x": lm.x, "y": lm.y, "z": lm.z, "v": lm.visibility
                        })
                
                json_payload = {"landmarks": landmarks_list}
                json_data = json.dumps(json_payload)
                json_bytes = json_data.encode('utf-8')
                json_len_data = struct.pack('<I', len(json_bytes))
                conn.sendall(json_len_data)
                conn.sendall(json_bytes)

            except ConnectionResetError:
                print("Unity ตัดการเชื่อมต่อ (ปกติ)")
                break 
            
            # --- ⭐️ 2. เพิ่มโค้ดให้ "ค้าง" ตอน Crash (สำหรับ Debug) ---
            except Exception as e:
                print("-----------------------------------")
                print(f"!!! CRASH: เกิดข้อผิดพลาดร้ายแรง !!!")
                print(f"ERROR: {e}")
                print("-----------------------------------")
                input("โปรแกรม Crash. กด Enter เพื่อปิดหน้าต่างนี้...") 
                break
                # --- ---------------------------------------------- ---
        
    pose.close()
    print("ปิดโปรแกรม Python")