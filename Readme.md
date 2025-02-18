
## **Description**
This repository implements a ground control station (GCS) for unmanned aerial vehicles (UAVs) using Python. It leverages Qt for Python (via PySide6) to create an interactive graphical user interface and uses pymavlink library to interface with UAVs. The project also integrates several libraries to provide a rich set of functionalities: 
- **Media and Video Handling:** Utilizes python-vlc (and requires VLC 64-bit installed) along with OpenCV to manage camera feeds and media playback.
- **Mapping and Visualization:** Employs folium for mapping capabilities enabling real-time map displays that can be crucial for UAV tracking.
- **Firebase Integration:** Contains components such as FirebaseUserTest.py and firebase-admin usage suggesting features for backend support or user authentication.
- **Modular Design:** The repository is organized into multiple modules (e.g. HomePage MapWidget IndicatorsPage TargetsPage) that handle different aspects of the control station ensuring a clean and maintainable codebase.

Overall this project is a practical tool for developers and UAV enthusiasts who want to experiment with or deploy a Python-based ground control station offering both the control mechanisms and visualization tools necessary for effective UAV operation.

## **Installation Guide**

### **1. Clone the Repository**
Open your terminal (or command prompt) and run:
```bash
git clone https://github.com/MahmutEsadErman/Ground-Control-Station-for-UAV.git
cd Ground-Control-Station-for-UAV
```

### **2. Install VLC**
This project uses VLC (64-bit version) for media handling.  
- **Linux:**  
  ```bash
  sudo apt-get install vlc
  ```
- **Windows/Mac:**  
  Download and install the latest 64-bit VLC from the [official website](https://www.videolan.org/vlc/).

### **3. (Optional) Set Up a Virtual Environment**
It’s a good practice to create a virtual environment to manage dependencies:
```bash
# Create a virtual environment (replace 'venv' with your preferred name)
python -m venv venv

# Activate the virtual environment:
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### **4. Install Python Dependencies**
Install the required Python packages using pip:
```bash
pip install python-vlc pyside6 opencv-python folium firebase-admin pymavlink
```
*Note: If you encounter any issues, ensure your pip is up-to-date by running `pip install --upgrade pip`.*

---

## **Usage Guide**

### **1. Running the Application**
Start the ground control station by executing:
```bash
python main.py
```
This should launch the interactive GUI built with Qt for Python.

### **2. Exploring the Interface**
- **HomePage:**  
  Displays real-time map and camera feed, and also a control panel to send commands to the UAV.
- **IndicatorsPage:**  
  Shows live UAV status indicators and telemetry data.
- **TargetsPage:**  
  Lists and manages UAV target information.

### **3. Connecting to a UAV**
- 

### **4. Media and Video Handling**
- The application integrates `python-vlc` and OpenCV to handle camera feeds and media playback.
- Ensure that your VLC installation is 64-bit and properly configured.
- Use the provided UI elements (such as in `CameraWidget.py`) to view or control media streams.

### **5. Firebase Integration**
- For backend support or user authentication, Firebase is integrated.
- Check `FirebaseUserTest.py` for testing and setup.
- Configure your Firebase credentials as needed following Firebase’s setup documentation.

### **6. Additional Customizations**
- The project is modular, so you can further develop or customize each component (e.g., adding new features to the HomePage or integrating additional sensors).
- Refer to the source files (like `AntennaTracker.py`, `MediaPlayer.py`, etc.) for more detailed functionality and integration points.

---

By following these steps, you should be able to set up, run, and begin exploring the capabilities of the Ground Control Station for UAVs. If you encounter any issues or need further customization, consider reviewing the inline comments within the source code or referring to the documentation of the individual libraries used.
