import io, sys

from PySide6 import QtWebEngineWidgets
from PySide6.QtCore import Qt
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


class MapWidget(QtWebEngineWidgets.QWebEngineView):
    mission = []

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
        data.seek(0)
        data.write(html.encode())

        # To Get Java Script Console Messages
        self.map_page = self.WebEnginePage()
        self.setPage(self.map_page)

        # To Display the Map
        self.resize(800, 600)
        self.setHtml(data.getvalue().decode())

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
                    });
                    
                var targetIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    });
                    
                var userIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                    });
                    
                // Adding First Marker
                var mymarker = L.marker(
                        [41.27442, 28.727317],
                        {}
                    ).addTo(map);
                
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
                }
                
                // To plan a mission putting waypoints to the places that we want uav to go
                var waypointNumber = 0;
                var waypoints = [];
                var lines = [];
                function putWaypointEvent(e) {
                    putWaypoint(e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4))
                }
                
                function putWaypoint(lat, lng) {
                    var marker = L.marker(
                        [lat, lng],
                        {}
                    ).addTo(map);
                    
                    // Add lines between last to waypoints
                    if(waypoints.length > 0){
                        points = [waypoints[waypoints.length-1].getLatLng(), marker.getLatLng()];
                        line = L.polyline(points, {color: 'red'}).addTo(map);
                        lines.push(line);
                    }
                    waypoints.push(marker);
                }
                
                var rect = 0;
                var corners = 0;
                function drawRectangle(e) {
                    if (corners.length == 0) {
                        corners.push(e.latlng);
                    } else if (corners.length == 1){
                        corners.push(e.latlng);
                        rect = L.rectangle(corners, {color: "#ff7800", weight: 1}).addTo(map);
                    } else {
                        corners = [];
                        corners.push(e.latlng);
                        map.removeLayer(rect);
                    }
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
                        for(let i = 0; i < 2; i++){
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
                    if (rect != 0){
                        map.removeLayer(rect);
                    }
                }
                
                // Initial mode for clicking on the map
                map.on('click', moveMarkerByClick);
                
                // end custom code
        ''' % (map_variable_name, uav_icon_base64, target_marker_base64, mobileuser_marker_base64)


if __name__ == "__main__":
    # create variables
    istanbulhavalimani = [41.27442, 28.727317]

    # Display the Window
    app = QApplication([])
    widget = MapWidget(istanbulhavalimani)
    widget.show()

    sys.exit(app.exec())
