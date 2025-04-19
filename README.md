🚦 Traffic Management System 
(using OpenCV)
This project is a real-time traffic monitoring system that detects overspeeding vehicles using OpenCV and YOLO (Ultralytics). It then sends an e-challan to the registered number of the vehicle.

🚀 Features:

Vehicle Detection using YOLOv8

Speed Estimation based on object tracking

Automatic E-Challan Generation using Twilio SMS

Logs Every Event to logs/output.log

Video Processing & Real-Time Monitoring

📂 Folder Structure
bash
Copy
Edit
Traffic-management/
│── README.md                # 📄 Project Documentation
│── requirements.txt         # 📌 Required Python dependencies
│── src/                     # 🚀 Source Code
│   ├── main.py              # 🔹 Main Execution File
│   ├── vehicle_detection.py # 🔹 Detects Vehicles
│   ├── speed_calculation.py # 🔹 Computes Speed
│   ├── challan.py           # 🔹 Sends E-Challan
│── data/                    # 📂 Video Data
│   ├── traffic.mp4          # 📽️ Traffic Video Input
│── logs/                    # 📂 Logs Storage
│   ├── output.log           # 📝 System Logs
│── venv/                    # 🐍 Virtual Environment
📌 Prerequisites
Make sure you have Python 3.8+ installed. You can check your version using:

bash
Copy
Edit
python --version

🔧 Setup Instructions

1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/Traffic-management.git
cd Traffic-management

2️⃣ Create a Virtual Environment (Recommended)
For Windows:
powershell
Copy
Edit
python -m venv venv
venv\Scripts\activate
For macOS/Linux:
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate

3️⃣ Install Required Dependencies

bash
Copy
Edit
pip install -r requirements.txt
If you get ModuleNotFoundError, manually install missing packages:

bash
Copy
Edit
pip install opencv-python twilio ultralytics numpy
🚀 Running the Project
Run the script to start traffic monitoring:

bash
Copy
Edit
python src/main.py
📝 Viewing Logs
To monitor logs in real-time, run:

bash
Copy
Edit
tail -f logs/output.log  # Linux/macOS
Get-Content logs/output.log -Wait  # Windows PowerShell

📌 How It Works

1️⃣ Loads traffic.mp4 and starts vehicle detection
2️⃣ Tracks vehicles and estimates their speed
3️⃣ If speed exceeds 60 km/h, logs the event and sends an e-challan
4️⃣ Outputs video with detected vehicles in an OpenCV window
5️⃣ Logs everything in logs/output.log

🛠 Troubleshooting
1️⃣ No Logs in output.log?
✅ Solution: Run these commands to ensure logging is working:

bash
Copy
Edit
echo "Test log entry" >> logs/output.log
cat logs/output.log
If it’s empty, check main.py for this logging setup:

python
Copy
Edit
import logging
import os
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "output.log")
logging.basicConfig(filename=log_file, level=logging.INFO)
logging.info("🚦 Traffic Monitoring System Started 🚦")
2️⃣ ModuleNotFoundError: No module named 'cv2'?
✅ Solution: Install OpenCV manually:

bash
Copy
Edit
pip install opencv-python
3️⃣ ModuleNotFoundError: No module named 'ultralytics'?
✅ Solution: Install YOLO package:

bash
Copy
Edit
pip install ultralytics
4️⃣ Video Not Playing?
✅ Solution: Try a different video path in main.py:

python
Copy
Edit
video_path = "data/traffic.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video file.")
📜 License
This project is licensed under the MIT License.

👨‍💻 Author
Hritika Khattar
Devyani Sisodia

