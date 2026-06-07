import io, sys

from PySide6 import QtWebEngineWidgets
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QPushButton
import folium
from folium.plugins import MousePosition

# Make Icon
from PIL import Image
import base64


def image_to_base64(image_path, size=(100, 100)):
    with Image.open(image_path) as img:
        img = img.resize(size)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()


def icon_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


uav_icon_base64 = icon_to_base64('uifolder/assets/icons/uav.png')
mobileuser_marker_base64 = icon_to_base64('uifolder/assets/icons/mobileuser.png')
target_marker_base64 = icon_to_base64('uifolder/assets/icons/target.png')
home_icon_base64 = icon_to_base64('uifolder/assets/icons/antenna.png')


class MapWidget(QtWebEngineWidgets.QWebEngineView):
    mission = []
    boundaries = []

    def __init__(self, center_coord, starting_zoom=13):
        super().__init__()
        MapWidget.marker_coord = center_coord
        self.fmap = folium.Map(location=center_coord,
                               zoom_start=starting_zoom)

        # Show mouse position in bottom right
        MousePosition().add_to(self.fmap)

        # store the map to a file
        data = io.BytesIO()
        self.fmap.save('map.html')
        self.fmap.save(data, close_file=False)

        # reading the folium file
        html = data.getvalue().decode()

        # find variable names
        self.map_variable_name = self.find_variable_name(html, "map_")

        # determine scripts indices
        endi = html.rfind("</script>")

        # inject code
        html = html[:endi - 1] + self.custom_code(self.map_variable_name) + html[endi:]
        # inject referrer policy for OSM tiles
        html = html.replace("<head>", "<head>\n    <meta name=\"referrer\" content=\"strict-origin-when-cross-origin\"/>")
        data.seek(0)
        data.write(html.encode())

        # To Get Java Script Console Messages
        self.map_page = self.WebEnginePage()
        self.setPage(self.map_page)

        # To Display the Map
        self.resize(800, 600)
        self.setHtml(data.getvalue().decode(), QUrl("http://localhost/"))

        # Add buttons
        self.btn_AllocateWidget = QPushButton(icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self)
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

        # self.loadFinished.connect(self.onLoadFinished)

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

    class WebEnginePage(QWebEnginePage):
        def __init__(self):
            super().__init__()
            self.markers_pos = []

        def javaScriptConsoleMessage(self, level, msg, line, sourceID):
            if msg[0] == 'm':
                MapWidget.mission = []
                pairs = msg[1:].split('&')
                for pair in pairs:
                    MapWidget.mission.append(list(map(float, pair.split(','))))
                print("mission: ", MapWidget.mission)
            elif msg[0] == 'b':
                MapWidget.boundaries = []
                if len(msg) > 1:
                    pairs = msg[1:].split('&')
                    for pair in pairs:
                        MapWidget.boundaries.append(list(map(float, pair.split(','))))
                print("boundaries: ", MapWidget.boundaries)
            else:
                self.markers_pos = msg.split(',')
                print(msg)

    def find_variable_name(self, html, name_start):
        variable_pattern = "var "
        pattern = variable_pattern + name_start

        starting_index = html.find(pattern) + len(variable_pattern)
        tmp_html = html[starting_index:]
        ending_index = tmp_html.find(" =") + starting_index

        return html[starting_index:ending_index]

    def custom_code(self, map_variable_name):
        return '''
                // custom code
                
                // Rotated Marker Function
                (function() {
                    // save these original methods before they are overwritten
                    var proto_initIcon = L.Marker.prototype._initIcon;
                    var proto_setPos = L.Marker.prototype._setPos;
                
                    var oldIE = (L.DomUtil.TRANSFORM === 'msTransform');
                
                    L.Marker.addInitHook(function () {
                        var iconOptions = this.options.icon && this.options.icon.options;
                        var iconAnchor = iconOptions && this.options.icon.options.iconAnchor;
                        if (iconAnchor) {
                            iconAnchor = (iconAnchor[0] + 'px ' + iconAnchor[1] + 'px');
                        }
                        this.options.rotationOrigin = this.options.rotationOrigin || iconAnchor || 'center bottom' ;
                        this.options.rotationAngle = this.options.rotationAngle || 0;
                
                        // Ensure marker keeps rotated during dragging
                        this.on('drag', function(e) { e.target._applyRotation(); });
                    });
                
                    L.Marker.include({
                        _initIcon: function() {
                            proto_initIcon.call(this);
                        },
                
                        _setPos: function (pos) {
                            proto_setPos.call(this, pos);
                            this._applyRotation();
                        },
                
                        _applyRotation: function () {
                            if(this.options.rotationAngle) {
                                this._icon.style[L.DomUtil.TRANSFORM+'Origin'] = this.options.rotationOrigin;
                
                                if(oldIE) {
                                    // for IE 9, use the 2D rotation
                                    this._icon.style[L.DomUtil.TRANSFORM] = 'rotate(' + this.options.rotationAngle + 'deg)';
                                } else {
                                    // for modern browsers, prefer the 3D accelerated version
                                    this._icon.style[L.DomUtil.TRANSFORM] += ' rotateZ(' + this.options.rotationAngle + 'deg)';
                                }
                            }
                        },
                
                        setRotationAngle: function(angle) {
                            this.options.rotationAngle = angle;
                            this.update();
                            return this;
                        },
                
                        setRotationOrigin: function(origin) {
                            this.options.rotationOrigin = origin;
                            this.update();
                            return this;
                        }
                    });
                })();
                // Rotated Marker part is taken from this repo: https://github.com/bbecquet/Leaflet.RotatedMarker
                // Huge thanks to its contributors
                
                // Take the generated map variable from folium
                var map = %s;
                
                
                var uavIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]
                    });
                    
                var targetIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]
                    });
                    
                var userIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]
                    });
                
                var homeIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    iconAnchor: [20, 20]
                    });
                    
                var waypointIcon = L.icon({
                    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-icon.png',
                    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-icon-2x.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                    
                // Adding First Marker
                var mymarker = L.marker(
                        [41.27442, 28.727317],
                        {icon: waypointIcon}
                    ).addTo(map);
                    
                // UAV Trajectory Line
                var uavTrajectory = L.polyline([], {color: 'blue', weight: 3}).addTo(map);
                var maxTrajectoryPoints = 2000; // Performans için maksimum nokta sınırı
                
                function updateUavPosition(lat, lng, heading) {
                    if (typeof uavMarker !== 'undefined') {
                        uavMarker.setLatLng([lat, lng]);
                        uavMarker.setRotationAngle(heading - 45);
                        
                        var latlngs = uavTrajectory.getLatLngs();
                        if (latlngs.length === 0) {
                            uavTrajectory.addLatLng([lat, lng]);
                        } else {
                            var lastPoint = latlngs[latlngs.length - 1];
                            // Çok küçük titreşimleri ve hareketsiz anları kaydetmemek için 1 metre mesafe kontrolü
                            if (lastPoint.distanceTo([lat, lng]) > 1.0) { 
                                uavTrajectory.addLatLng([lat, lng]);
                                // Eğer sınır aşılırsa en eski noktayı sil (kuyruk mantığı)
                                if (latlngs.length > maxTrajectoryPoints) {
                                    latlngs.shift(); 
                                    uavTrajectory.setLatLngs(latlngs);
                                }
                            }
                        }
                    }
                }
                
                function clearTrajectory() {
                    uavTrajectory.setLatLngs([]);
                }
                
                // Some Functions To Make Map Interactive
                function moveMarkerByClick(e) {
                    console.log(e.latlng.lat.toFixed(4) + "," +e.latlng.lng.toFixed(4));
                    mymarker.setLatLng([e.latlng.lat, e.latlng.lng])
                }
                
                function undoWaypoint() {
                    if(waypoints.length >0)
                        waypoints.pop().remove();
                    if(lines.length > 0)
                        lines.pop().remove();
                    if(distanceLabels.length > 0)
                        distanceLabels.pop().remove();
                        
                    if(cornerMarkers.length > 0) {
                        cornerMarkers.pop().remove();
                        corners.pop();
                        if (areaPolygon != 0) {
                            map.removeLayer(areaPolygon);
                            areaPolygon = 0;
                        }
                        if (corners.length >= 2) {
                            areaPolygon = L.polygon(corners, {color: "#ff7800", weight: 2, fill: false}).addTo(map);
                        }
                    }
                    
                    // Undo for distance measure mode
                    if (typeof distMeasurePoints !== 'undefined') {
                        if (distMeasurePoints.length > 0) {
                            distMeasurePoints.pop();
                            distMeasureMarkers.pop().remove();
                        } else if (distMeasureLines.length > 0) {
                            distMeasureLines.pop().remove();
                            distMeasureLabels.pop().remove();
                            distMeasureMarkers.pop().remove();
                            distMeasureMarkers.pop().remove();
                        }
                    }
                }
                
                // To plan a mission putting waypoints to the places that we want uav to go
                var waypointNumber = 0;
                var waypoints = [];
                var lines = [];
                var distanceLabels = [];
                function putWaypointEvent(e) {
                    putWaypoint(e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4))
                }
                
                function putWaypoint(lat, lng) {
                    var marker = L.marker(
                        [lat, lng],
                        {icon: waypointIcon}
                    ).addTo(map);
                    
                    // Add lines between last to waypoints
                    if(waypoints.length > 0){
                        var prevMarker = waypoints[waypoints.length-1];
                        var currentLatLng = L.latLng(lat, lng);
                        var points = [prevMarker.getLatLng(), currentLatLng];
                        var line = L.polyline(points, {color: 'red'}).addTo(map);
                        lines.push(line);
                        
                        var distance = prevMarker.getLatLng().distanceTo(currentLatLng);
                        var midLat = (prevMarker.getLatLng().lat + currentLatLng.lat) / 2;
                        var midLng = (prevMarker.getLatLng().lng + currentLatLng.lng) / 2;
                        
                        var textIcon = L.divIcon({
                            className: 'distance-label',
                            html: '<div style="background-color: white; padding: 2px 5px; border-radius: 3px; font-weight: bold; border: 1px solid black; text-align: center; white-space: nowrap;">' + distance.toFixed(1) + ' m</div>',
                            iconSize: null
                        });
                        var labelMarker = L.marker([midLat, midLng], {icon: textIcon}).addTo(map);
                        distanceLabels.push(labelMarker);
                    }
                    waypoints.push(marker);
                }
                
                // Distance Measure Mode Variables and Function
                var distMeasurePoints = [];
                var distMeasureLines = [];
                var distMeasureLabels = [];
                var distMeasureMarkers = [];

                function distanceMeasureClick(e) {
                    var marker = L.marker([e.latlng.lat, e.latlng.lng], {icon: waypointIcon}).addTo(map);
                    distMeasureMarkers.push(marker);
                    distMeasurePoints.push(e.latlng);
                    
                    if (distMeasurePoints.length === 2) {
                        var points = [distMeasurePoints[0], distMeasurePoints[1]];
                        var line = L.polyline(points, {color: 'green', weight: 4}).addTo(map);
                        distMeasureLines.push(line);
                        
                        var distance = distMeasurePoints[0].distanceTo(distMeasurePoints[1]);
                        var midLat = (distMeasurePoints[0].lat + distMeasurePoints[1].lat) / 2;
                        var midLng = (distMeasurePoints[0].lng + distMeasurePoints[1].lng) / 2;
                        
                        var textIcon = L.divIcon({
                            className: 'distance-label',
                            html: '<div style="background-color: lightgreen; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 2px solid darkgreen; text-align: center; white-space: nowrap;">' + distance.toFixed(1) + ' m</div>',
                            iconSize: null
                        });
                        var labelMarker = L.marker([midLat, midLng], {icon: textIcon}).addTo(map);
                        distMeasureLabels.push(labelMarker);
                        
                        distMeasurePoints = []; // Reset for next measurement pair
                    }
                }
                
                var squareIcon = L.divIcon({
                    className: 'custom-square-marker',
                    html: '<div style="background-color: blue; width: 15px; height: 15px; border: 2px solid white;"></div>',
                    iconSize: [15, 15],
                    iconAnchor: [7, 7]
                });
                
                var areaPolygon = 0;
                var corners = [];
                var cornerMarkers = [];
                
                function drawRectangle(e) {
                    corners.push(e.latlng);
                    var marker = L.marker([e.latlng.lat, e.latlng.lng], {icon: squareIcon}).addTo(map);
                    cornerMarkers.push(marker);
                    
                    if (areaPolygon != 0) {
                        map.removeLayer(areaPolygon);
                    }
                    
                    if (corners.length >= 2) {
                        areaPolygon = L.polygon(corners, {color: "#ff7800", weight: 2, fill: false}).addTo(map);
                    }
                }
                
                function sendBoundaries() {
                    var msg = "b";
                    for(let i = 0; i < corners.length; i++){
                        msg += corners[i].lat.toFixed(4) + "," + corners[i].lng.toFixed(4) ;
                        if (i < corners.length-1){
                            msg += "&"
                        }
                    }
                    console.log(msg);
                }
                
                function setMission(mission_type) {
                    var msg = "m";
                    if (mission_type){ // waypoints
                        for(let i = 0; i < waypoints.length; i++){
                            msg += waypoints[i].getLatLng().lat.toFixed(4) + "," + waypoints[i].getLatLng().lng.toFixed(4) ;
                            if (i < waypoints.length-1){
                                msg += "&"
                            }
                        }
                    }
                    else{ // exploration
                        for(let i = 0; i < corners.length; i++){
                            msg += corners[i].lat.toFixed(4) + "," + corners[i].lng.toFixed(4) ;
                            if (i < corners.length-1){
                                msg += "&"
                            }
                        }
                    }
                    console.log(msg);
                }
                
                function clearAll() {
                    if (waypoints.length > 0){
                        for(let i = 0; i < waypoints.length; i++){
                            waypoints[i].remove();
                        }
                        waypoints = [];
                    }
                    if (lines.length > 0){
                        for(let i = 0; i < lines.length; i++){
                            lines[i].remove();
                        }
                        lines = [];
                    }
                    if (distanceLabels.length > 0){
                        for(let i = 0; i < distanceLabels.length; i++){
                            distanceLabels[i].remove();
                        }
                        distanceLabels = [];
                    }
                    if (areaPolygon != 0){
                        map.removeLayer(areaPolygon);
                        areaPolygon = 0;
                    }
                    if (cornerMarkers && cornerMarkers.length > 0) {
                        for(let i = 0; i < cornerMarkers.length; i++){
                            cornerMarkers[i].remove();
                        }
                        cornerMarkers = [];
                    }
                    corners = [];
                    if (typeof clearTrajectory !== 'undefined') {
                        clearTrajectory();
                    }
                    
                    // Clear distance measure tools
                    if (distMeasureMarkers.length > 0) {
                        for(let i=0; i<distMeasureMarkers.length; i++) distMeasureMarkers[i].remove();
                        distMeasureMarkers = [];
                    }
                    if (distMeasureLines.length > 0) {
                        for(let i=0; i<distMeasureLines.length; i++) distMeasureLines[i].remove();
                        distMeasureLines = [];
                    }
                    if (distMeasureLabels.length > 0) {
                        for(let i=0; i<distMeasureLabels.length; i++) distMeasureLabels[i].remove();
                        distMeasureLabels = [];
                    }
                    distMeasurePoints = [];
                }
                
                // Initial mode for clicking on the map
                map.on('click', moveMarkerByClick);
                
                // end custom code
        ''' % (map_variable_name, uav_icon_base64, target_marker_base64, mobileuser_marker_base64, home_icon_base64)


if __name__ == "__main__":
    # create variables
    istanbulhavalimani = [41.27442, 28.727317]

    # Display the Window
    app = QApplication([])
    widget = MapWidget(istanbulhavalimani)
    widget.show()

    sys.exit(app.exec())
