import io, sys
from PySide6 import QtWebEngineWidgets
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication
import folium

# Make Icon
import base64
from PIL import Image


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


uav_icon_base64 = image_to_base64('/home/esad/Desktop/Coding/GroundControlStation/icons/uav.png')


class MapWidget(QtWebEngineWidgets.QWebEngineView):
    marker_coord = None

    def __init__(self, center_coord, starting_zoom=13, parent=None):
        super().__init__(parent)
        MapWidget.marker_coord = center_coord
        self.fmap = folium.Map(location=center_coord,
                               zoom_start=starting_zoom)

        # folium features
        folium.LatLngPopup().add_to(self.fmap)

        # store the map to a file
        data = io.BytesIO()
        self.fmap.save(data, close_file=False)

        # reading the folium file
        html = data.getvalue().decode()

        # find variable names
        self.map_variable_name = self.find_variable_name(html, "map_")
        self.popup_variable_name = self.find_variable_name(html, "lat_lng_popup_")

        # determine popup function indicies
        pstart, pend = self.find_popup_slice(html)

        # inject code
        html = html[:pstart] + self.custom_code(self.popup_variable_name, self.map_variable_name) + html[pend:]

        data.seek(0)
        data.write(html.encode())

        # To Get Java Script Console Messages
        self.map_page = self.WebEnginePage(self)
        self.setPage(self.map_page)

        # self.map_page.setHtml(data.getvalue().decode())

        # To Display the Map
        self.resize(800, 600)
        self.setHtml(data.getvalue().decode())

        self.loadFinished.connect(self.onLoadFinished)

    class WebEnginePage(QWebEnginePage):
        def javaScriptConsoleMessage(self, level, msg, line, sourceID):
            MapWidget.marker_coord = msg.split(",")
            print(MapWidget.marker_coord)

    def onLoadFinished(self):
        # add marker
        self.page().runJavaScript("""
                var uavIcon = L.icon({
                    iconUrl: 'data:image/png;base64,%s', 
                    iconSize: [40, 40],
                });
        
                var uavMarker = L.marker(
                            [41.27442, 28.727317],
                            {icon: uavIcon,
                            },
                            
                        ).addTo(%s);
                uavMarker.setRotationAngle(-45)
                """ % (uav_icon_base64, self.map_variable_name)
                                  )

    def find_popup_slice(self, html):
        """
        Find the starting and ending index of popup function
        """

        pattern = "function latLngPop(e)"

        # starting index
        starting_index = html.find(pattern)

        #
        tmp_html = html[starting_index:]

        #
        found = 0
        index = 0
        opening_found = False
        while not opening_found or found > 0:
            if tmp_html[index] == "{":
                found += 1
                opening_found = True
            elif tmp_html[index] == "}":
                found -= 1

            index += 1

        # determine the ending index of popup function
        ending_index = starting_index + index

        return starting_index, ending_index

    def find_variable_name(self, html, name_start):
        variable_pattern = "var "
        pattern = variable_pattern + name_start

        starting_index = html.find(pattern) + len(variable_pattern)
        tmp_html = html[starting_index:]
        ending_index = tmp_html.find(" =") + starting_index

        return html[starting_index:ending_index]

    def custom_code(self, popup_variable_name, map_variable_name):
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
                
                
                var mymarker = L.marker(
                        [41.27442, 28.727317],
                        {}
                    ).addTo(%s);
                
                function latLngPop(e) {
                    console.log(e.latlng.lat.toFixed(4) + "," +e.latlng.lng.toFixed(4));
                    mymarker.setLatLng([e.latlng.lat, e.latlng.lng])
                }
                // end custom code
        ''' % (map_variable_name)


if __name__ == "__main__":
    # create variables
    istanbulhavalimani = [41.27442, 28.727317]

    # Display the Window
    app = QApplication([])
    widget = MapWidget(istanbulhavalimani)
    widget.show()

    sys.exit(app.exec())
