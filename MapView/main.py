import asyncio
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label

from lineMapLayer import LineMapLayer
from datasource import Datasource
# from file_datasource import FileDatasource
from kivy_garden.mapview import *

class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapview = None
        self.car_marker = None
        self.line_layer = None

        # self.file_datasource = None
        self.store_datasource = None

        # Track markers for different road conditions
        self.pothole_markers = []
        self.bump_markers = []


    def build(self):
        # Initialize  data sources
        # self.file_datasource = FileDatasource("data.csv", user_id=1)
        self.store_datasource = Datasource(user_id=1)
        # Initialize map centered on Kyiv
        self.mapview = MapView(zoom=12, lat=50.4501, lon=30.5234)

        # Initialize line layer for tracking
        self.line_layer = LineMapLayer(color=[0, 0, 1, 1])
        self.mapview.add_layer(self.line_layer)

        # Initiali


        # Initialize car marker
        self.car_marker = MapMarker()
        self.mapview.add_marker(self.car_marker)

        # Start updates
        Clock.schedule_interval(self.update, 1.0)  # Update every second

        # Add a label for connection status (optional)
        self.status_label = Label(text="Connecting...", font_size='20sp',
                                  pos_hint={'top': 1, 'x': 0}, color=[1,1,1,1])  # White color
        self.mapview.add_widget(self.status_label)

        return self.mapview

    def on_start(self):
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.store_datasource.connect_to_server())
            loop.close()  # Close the loop after the coroutine completes

        threading.Thread(target=run_loop, daemon=True).start()

    def update(self, *args):
        # Get new points from both sources
        # file_points = self.file_datasource.get_new_points()
        store_points = self.store_datasource.get_new_points()

        # all_points = file_points + store_points
        all_points = store_points # Use only store points
        if self.store_datasource.connection_status:
            self.status_label.text = f"Status: {self.store_datasource.connection_status}"


        for point in all_points:
            lat, lon, road_state = point

            # Update car marker
            self.update_car_marker((lat, lon))

            # Add point to line layer
            self.line_layer.add_point((lat, lon))

            # Add markers based on road state
            if road_state == "POTHOLE":
                self.set_pothole_marker((lat, lon))
            elif road_state == "BUMP":
                self.set_bump_marker((lat, lon))


    def update_car_marker(self, point):
        lat, lon = point
        self.car_marker.lat = lat
        self.car_marker.lon = lon

    def set_pothole_marker(self, point):
        lat, lon = point
        try:
            marker = MapMarker(lat=lat, lon=lon, source='images/pothole.png')
        except:
            # Use default marker if image not found
            marker = MapMarker(lat=lat, lon=lon)
        self.mapview.add_marker(marker)
        self.pothole_markers.append(marker)

    def set_bump_marker(self, point):
        lat, lon = point
        try:
            marker = MapMarker(lat=lat, lon=lon, source='images/bump.png')
        except:
            # Use default marker if image not found
            marker = MapMarker(lat=lat, lon=lon)
        self.mapview.add_marker(marker)
        self.bump_markers.append(marker)

if __name__ == '__main__':
    MapViewApp().run()