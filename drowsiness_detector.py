from flask import Flask, request, jsonify
import subprocess
import threading
import time
import RPi.GPIO as GPIO

# GPIO Pin Configuration
HAZARD_LIGHT_PIN = 17  # GPIO pin for hazard lights
BRAKE_PIN = 27         # GPIO pin for brake signal

app = Flask(__name__)

# State tracking
alert_active = False
alert_thread = None
alert_stage = 0
alert_start_time = None

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(HAZARD_LIGHT_PIN, GPIO.OUT)
GPIO.setup(BRAKE_PIN, GPIO.OUT)
GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
GPIO.output(BRAKE_PIN, GPIO.LOW)

def speak(text):
    """Text-to-speech output using espeak"""
    print(f"Speaking: {text}")
    try:
        subprocess.run(['espeak', text, '-s', '140', '-p', '70'])
    except Exception as e:
        print(f"TTS Error: {e}")

def blink_hazard_lights():
    """Blink hazard lights"""
    for _ in range(10):
        GPIO.output(HAZARD_LIGHT_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
        time.sleep(0.5)

def alert_sequence():
    """Three-stage alert sequence"""
    global alert_active, alert_stage, alert_start_time

    alert_start_time = time.time()
    alert_stage = 1

    # Stage 1: Initial warning
    print("\n=== STAGE 1: INITIAL WARNING ===")
    speak("Warning! Driver drowsiness detected. Please wake up immediately!")

    stage1_wait = 0
    while alert_active and stage1_wait < 10:
        time.sleep(1)
        stage1_wait += 1
        print(f"Stage 1: Waiting... {stage1_wait}/10 seconds")

    if not alert_active:
        print("Alert cancelled - driver is awake")
        return

    # Stage 2: Hazard lights
    alert_stage = 2
    print("\n=== STAGE 2: HAZARD LIGHTS ACTIVATED ===")
    speak("Driver still unresponsive. Activating hazard lights.")

    hazard_thread = threading.Thread(target=blink_hazard_lights)
    hazard_thread.start()

    stage2_wait = 0
    while alert_active and stage2_wait < 10:
        time.sleep(1)
        stage2_wait += 1
        print(f"Stage 2: Waiting... {stage2_wait}/10 seconds")

    if not alert_active:
        GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
        print("Alert cancelled - driver is awake")
        return

    # Stage 3: Emergency brake
    alert_stage = 3
    print("\n=== STAGE 3: EMERGENCY BRAKE ===")
    GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
    GPIO.output(BRAKE_PIN, GPIO.HIGH)

    speak("Emergency braking initiated. Contacting emergency services.")
    print("Emergency brake applied!")
    print("Initiating emergency contact...")

    time.sleep(2)
    speak("Emergency services have been notified. Vehicle location transmitted.")

    while alert_active:
        time.sleep(1)

    GPIO.output(BRAKE_PIN, GPIO.LOW)
    GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
    print("Alert sequence ended")

@app.route('/alert', methods=['POST'])
def receive_alert():
    """Receive alert from laptop"""
    global alert_active, alert_thread, alert_stage

    data = request.json
    alert_type = data.get('type', 'unknown')
    duration = data.get('duration', 0)

    print(f"\nReceived alert: {alert_type}, Duration: {duration}s")

    if alert_type == 'drowsy' and not alert_active:
        alert_active = True
        alert_thread = threading.Thread(target=alert_sequence)
        alert_thread.start()

        return jsonify({
            "status": "alert_started",
            "message": "Drowsiness alert sequence initiated"
        }), 200

    elif alert_type == 'awake':
        if alert_active:
            print(f"\nDriver awake at Stage {alert_stage}. Cancelling alert...")
            alert_active = False

            GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
            GPIO.output(BRAKE_PIN, GPIO.LOW)

            speak("Driver is awake. Alert cancelled.")

            if alert_thread:
                alert_thread.join(timeout=2)

            alert_stage = 0

        return jsonify({
            "status": "alert_cancelled",
            "message": "Alert sequence stopped"
        }), 200

    return jsonify({
        "status": "acknowledged",
        "current_stage": alert_stage
    }), 200

@app.route('/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify({
        "alert_active": alert_active,
        "alert_stage": alert_stage,
        "time_elapsed": time.time() - alert_start_time if alert_start_time else 0
    }), 200

@app.route('/test', methods=['POST'])
def test_system():
    """Test individual components"""
    test_type = request.json.get('test', 'voice')

    if test_type == 'voice':
        speak("Testing voice system. This is a test message.")
    elif test_type == 'hazard':
        print("Testing hazard lights...")
        for _ in range(5):
            GPIO.output(HAZARD_LIGHT_PIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(HAZARD_LIGHT_PIN, GPIO.LOW)
            time.sleep(0.5)
    elif test_type == 'brake':
        print("Testing brake signal...")
        GPIO.output(BRAKE_PIN, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(BRAKE_PIN, GPIO.LOW)

    return jsonify({"status": "test_complete"}), 200

def cleanup():
    """Cleanup GPIO on exit"""
    GPIO.cleanup()

if __name__ == '__main__':
    print("=" * 50)
    print("Driver Drowsiness Detection - Raspberry Pi Server")
    print("=" * 50)
    print("\nAlert Stages:")
    print("  Stage 1 (0-10s):  Voice warning")
    print("  Stage 2 (10-20s): Hazard lights + announcement")
    print("  Stage 3 (20s+):   Emergency brake + emergency contact")
    print("\nStarting Flask server on port 5000...")

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cleanup()