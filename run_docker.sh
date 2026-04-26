#!/bin/bash

# Yerel bilgisayarın grafik arayüzüne docker'ın erişimine (X11) izin ver
xhost +local:root

# İmajı derle (Sadece ilk çalıştırışta uzun sürer)
docker build -t gcs_ros2_humble .

# Konteyneri başlat ve X11 soketlerini bağla (GUI'nin açılabilmesi için)
docker run -it --rm \
    --name gcs_container \
    --net=host \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --device="/dev/video0:/dev/video0" \
    gcs_ros2_humble

# İzinleri eski haline geri getir
xhost -local:root
