#!/bin/bash

# Yerel bilgisayarın grafik arayüzüne docker'ın erişimine (X11) izin ver
xhost +local:root

# İmajı derle (Sadece Dockerfile değiştiğinde otomatik çalışır)
if [ ! -f .docker_build_time ] || [ Dockerfile -nt .docker_build_time ]; then
    echo "Dockerfile güncellendi veya ilk kez çalışıyor. İmaj derleniyor..."
    docker build -t gcs_ros2_humble .
    touch .docker_build_time
else
    echo "Dockerfile değişmemiş, mevcut imaj kullanılıyor..."
fi

# Konteyneri başlat ve X11 soketlerini bağla (GUI'nin açılabilmesi için)
docker run -it --rm \
    --name gcs_container \
    --net=host \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="$(pwd):/app:rw" \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /dev:/dev \
    --runtime=nvidia \
    --gpus all \
    gcs_ros2_humble

# İzinleri eski haline geri getir
xhost -local:root
