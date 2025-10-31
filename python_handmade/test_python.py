import cv2

# หากล้องทั้งหมด (ตรวจสอบ 10 กล้องแรก)
def find_cameras():
    available_cameras = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"✅ Camera {i} found")
            cap.release()
        else:
            print(f"❌ Camera {i} not available")
    
    return available_cameras

# ใช้งาน
print("Searching for cameras...")
cameras = find_cameras()
print(f"\n📷 Found {len(cameras)} camera(s): {cameras}")

# ทดสอบเปิดกล้องแรก
if cameras:
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()