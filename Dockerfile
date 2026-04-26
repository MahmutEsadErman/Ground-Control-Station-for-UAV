FROM osrf/ros:humble-desktop-full

# Sistem paketlerini güncelle ve Qt/GUI için gerekli olan kütüphaneleri yükle
RUN apt-get update && apt-get install -y \
    python3-pip \
    libxcb-cursor0 \
    libgl1-mesa-glx \
    vlc \
    && rm -rf /var/lib/apt/lists/*

# ROS 2 için gerekli MAVROS ve cv_bridge paketlerini yükle
RUN apt-get update && apt-get install -y \
    ros-humble-cv-bridge \
    ros-humble-mavros \
    ros-humble-mavros-extras && \
    wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh && \
    chmod a+x ./install_geographiclib_datasets.sh && \
    sudo ./install_geographiclib_datasets.sh && \
    rm -rf /var/lib/apt/lists/*

# Yer Kontrol İstasyonu için gerekli Python bağımlılıklarını kur
RUN pip3 install python-vlc pyside6 folium pymavlink msgpack
RUN pip3 install --force-reinstall "numpy<2" "opencv-python<4.9"

# Proje dosyalarını kopyalamak üzere çalışma dizinini ayarla
WORKDIR /app
COPY . .

# X11 yönlendirmesi için gerekli environment ayarları
ENV QT_X11_NO_MITSHM=1
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
ENV DISPLAY=$DISPLAY
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu"

# ROS 2 kaynaklarını otomatik olarak source et ve ana uygulamayı başlat
CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && python3 main.py"]
