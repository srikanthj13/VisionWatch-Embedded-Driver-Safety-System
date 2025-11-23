import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import requests
import time

# Configuration - CHANGE THIS TO YOUR RASPBERRY PI'S IP
RASPBERRY_PI_IP = "192.168.43.154"  # <<< CHANGE THIS
RASPBERRY_PI_PORT = 5000

# Eye Aspect Ratio threshold
EAR_THRESHOLD = 0.25

class DrowsinessDetector:
    def __init__(self):
        print("Initializing face detector...")
        # Initialize dlib face detector and landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        
        try:
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            print("✓ Face landmark model loaded")
        except Exception as e:
            print("✗ ERROR: Could not load shape_predictor_68_face_landmarks.dat")
            print("  Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            raise e
        
        # Eye landmark indices (dlib 68-point model)
        self.LEFT_EYE = list(range(36, 42))
        self.RIGHT_EYE = list(range(42, 48))
        
        # State tracking
        self.eye_closed_start_time = None
        self.alert_sent = False
        
    def eye_aspect_ratio(self, eye):
        """Calculate Eye Aspect Ratio (EAR)"""
        # Vertical distances
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        # Horizontal distance
        C = dist.euclidean(eye[0], eye[3])
        # EAR formula
        ear = (A + B) / (2.0 * C)
        return ear
    
    def get_landmarks(self, frame, rect):
        """Get facial landmarks from detected face"""
        shape = self.predictor(frame, rect)
        coords = np.zeros((68, 2), dtype=int)
        for i in range(68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        return coords
    
    def send_alert_to_pi(self, alert_type, duration):
        """Send alert to Raspberry Pi"""
        try:
            url = f"http://{RASPBERRY_PI_IP}:{RASPBERRY_PI_PORT}/alert"
            data = {
                "type": alert_type,
                "duration": duration
            }
            response = requests.post(url, json=data, timeout=2)
            if response.status_code == 200:
                print(f"✓ Alert sent to Pi: {alert_type}")
                return True
            else:
                print(f"✗ Pi responded with status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to Pi at {RASPBERRY_PI_IP}:{RASPBERRY_PI_PORT}")
            print("  Make sure Pi server is running and IP is correct!")
            return False
        except Exception as e:
            print(f"✗ Error sending alert: {e}")
            return False
    
    def process_frame(self, frame):
        """Process each frame for drowsiness detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray, 0)
        
        status = "ALERT"
        ear = 0.0
        
        if len(faces) > 0:
            # Process first detected face
            face = faces[0]
            landmarks = self.get_landmarks(gray, face)
            
            # Extract eye coordinates
            left_eye = landmarks[self.LEFT_EYE]
            right_eye = landmarks[self.RIGHT_EYE]
            
            # Calculate EAR for both eyes
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            # Draw eye contours (green)
            left_hull = cv2.convexHull(left_eye)
            right_hull = cv2.convexHull(right_eye)
            cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
            
            # Draw face rectangle
            cv2.rectangle(frame, 
                         (face.left(), face.top()), 
                         (face.right(), face.bottom()), 
                         (0, 255, 0), 2)
            
            # Check if eyes are closed
            if ear < EAR_THRESHOLD:
                if self.eye_closed_start_time is None:
                    self.eye_closed_start_time = time.time()
                    print("Eyes closing...")
                
                elapsed = time.time() - self.eye_closed_start_time
                
                if elapsed >= 5 and not self.alert_sent:
                    # Eyes closed for 5 seconds - send alert
                    print("\n" + "="*50)
                    print("⚠️  DROWSINESS DETECTED!")
                    print("="*50)
                    self.send_alert_to_pi("drowsy", elapsed)
                    self.alert_sent = True
                    status = "DROWSY - ALERT SENT"
                elif elapsed >= 5:
                    status = f"DROWSY - {elapsed:.1f}s"
                else:
                    status = f"EYES CLOSING - {elapsed:.1f}s"
            else:
                # Eyes open - reset
                if self.alert_sent:
                    # Send recovery signal
                    print("\n" + "="*50)
                    print("✓ Driver awake - Cancelling alert")
                    print("="*50)
                    self.send_alert_to_pi("awake", 0)
                
                self.eye_closed_start_time = None
                self.alert_sent = False
                status = "AWAKE"
        else:
            status = "NO FACE DETECTED"
            self.eye_closed_start_time = None
            self.alert_sent = False
        
        # Display information on frame
        cv2.putText(frame, f"Status: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Threshold: {EAR_THRESHOLD}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if self.alert_sent:
            # Red warning overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), 
                         (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            cv2.putText(frame, "!!! DROWSINESS ALERT !!!", 
                       (frame.shape[1]//2 - 200, frame.shape[0]//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        
        return frame

def main():
    print("\n" + "="*60)
    print("  DRIVER DROWSINESS DETECTION SYSTEM - LAPTOP CLIENT")
    print("="*60)
    print(f"\n📡 Raspberry Pi IP: {RASPBERRY_PI_IP}:{RASPBERRY_PI_PORT}")
    print("📹 Initializing webcam...")
    
    # Test connection to Pi
    try:
        response = requests.get(f"http://{RASPBERRY_PI_IP}:{RASPBERRY_PI_PORT}/status", timeout=2)
        print("✓ Connected to Raspberry Pi successfully!")
    except:
        print("⚠️  WARNING: Cannot connect to Raspberry Pi")
        print("   Make sure the Pi server is running first!")
        print("   Continuing anyway...\n")
    
    detector = DrowsinessDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ ERROR: Could not open webcam")
        return
    
    print("✓ Webcam initialized")
    print("\n" + "="*60)
    print("SYSTEM READY")
    print("="*60)
    print("\nInstructions:")
    print("  • Look at the camera")
    print("  • Close eyes for 5 seconds to trigger alert")
    print("  • Press 'q' to quit")
    print("\n")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("✗ Failed to grab frame")
            break
        
        # Process frame
        processed_frame = detector.process_frame(frame)
        
        # Display
        cv2.imshow("Driver Drowsiness Detection", processed_frame)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nShutting down...")
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ System stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()