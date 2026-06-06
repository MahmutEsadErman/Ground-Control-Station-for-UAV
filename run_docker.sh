#!/bin/bash

# X11 iznini ver
xhost +local:root

# Çakışmayı önlemek için eski konteyneri kesin olarak temizle
docker rm -f gcs_container 2>/dev/null || true

# Konteyneri başlat
docker run -it --rm \
    --name gcs_container \
    --net=host \
    --ipc=host \
    --privileged \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --env="QT_QPA_PLATFORM=xcb" \
    --env="QSG_RHI_BACKEND=opengl" \
    --env="LIBGL_ALWAYS_SOFTWARE=1" \
    --env="ROS_DOMAIN_ID=42" \
    --env="QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox --disable-gpu" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="/run/dbus/system_bus_socket:/run/dbus/system_bus_socket:ro" \
    --volume="$(pwd):/app:rw" \
    --device="/dev/dri:/dev/dri" \
    --device="/dev/video0:/dev/video0" \
    gcs_ros2_humble

# İzinleri geri al
xhost -local:root