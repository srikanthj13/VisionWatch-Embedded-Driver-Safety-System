# 🚗 VisionWatch: Driver Drowsiness Detection System

**Real-Time Fatigue Monitoring using Raspberry Pi and Computer Vision**

A cost-effective embedded safety system that detects driver drowsiness in real-time and triggers multi-stage voice alerts to prevent accidents caused by fatigue.

---

## 👥 Team Members

- **J. Srikanth**
- **Kunwar Vikramaaditya Singh Katheria**
- **Navya Pathak** 
- **Pronay Dutta** 
- **P. Sai Teja** 

---

## 📌 About The Project

Driver fatigue causes nearly **40% of highway accidents** in India [file:2]. VisionWatch addresses this critical safety issue by continuously monitoring a driver's eye activity using computer vision and alerting them before drowsiness leads to an accident [file:2].

The system uses a **laptop webcam** to track eye movements and calculates the **Eye Aspect Ratio (EAR)** [file:2]. When eyes remain closed for more than 5 seconds, it sends an alert to a **Raspberry Pi**, which triggers escalating voice warnings until the driver responds [file:2].

---

## ✨ Key Features

- **Real-time eye monitoring** using facial landmark detection [file:2]
- **Eye Aspect Ratio (EAR) calculation** to detect drowsiness [file:2]
- **Multi-stage alert system** with three escalating voice warnings [file:2]
- **Wireless communication** between laptop and Raspberry Pi via Wi-Fi [file:2]
- **Auto-reset functionality** when driver wakes up [file:2]
- **Affordable and scalable** - works with any vehicle [file:2]

---

## 🛠️ Technology Stack

**Hardware:**
- Laptop with webcam
- Raspberry Pi (Model 3B/4)
- Speaker (connected via AUX cable)
- Wi-Fi network [file:2]

**Software:**
- Python 3.x
- OpenCV - Video capture and processing
- dlib - Facial landmark detection
- Flask - HTTP server on Raspberry Pi
- pyttsx3/espeak - Text-to-speech alerts
- requests - Alert transmission [file:2]

---

## 🚀 How It Works

1. **Monitoring**: Laptop webcam continuously captures driver's face
2. **Detection**: Eye landmarks tracked and EAR calculated in real-time
3. **Alert Trigger**: If eyes closed > 5 seconds, laptop sends alert to Raspberry Pi
4. **Voice Response**: 
   - Stage 1: Initial voice warning
   - Stage 2: Urgent announcement with hazard lights
   - Stage 3: Emergency contact simulation
5. **Recovery**: System automatically cancels alert when driver wakes up [file:2]

---

## 📊 Testing Results

The system was successfully tested with:
- ✅ Accurate EAR-based drowsiness detection
- ✅ Reliable laptop-to-Raspberry Pi communication
- ✅ Consistent multi-stage voice alerts
- ✅ Stable performance across multiple test cycles
- ✅ No false positives or system crashes [file:2]

---

## 🎯 Applications

- Personal vehicles for long-distance travel
- Commercial trucks and buses
- Fleet management systems
- Driving schools and training centers
- Public road safety awareness programs [file:2]

---

## 🔮 Future Enhancements

- GPS integration for emergency location sharing
- Mobile app for remote monitoring
- Cloud-based event logging and analytics
- Multi-factor detection (yawning, head tilt, blink rate)
- Vehicle control integration for automatic braking
- Multilingual voice alerts [file:2]

---

## 📄 Documentation

For detailed technical information, methodology, complete code, testing procedures, and system architecture diagrams, please refer to the **[VisionWatch.pdf](VisionWatch.pdf)** included in this repository [file:2].

---

## 📧 Contact

For questions or collaboration opportunities, feel free to reach out to any of the team members via LinkedIn.

---

## ⚠️ Disclaimer

This is a prototype system designed for educational and research purposes. It should not replace professional driver assistance systems in production vehicles.

---

**Project Type:** Open-source prototype / Personal research project [file:2]

**License:** MIT

