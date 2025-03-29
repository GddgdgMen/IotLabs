import asyncio
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy_garden.mapview import MapView, MapMarker
from lineMapLayer import LineMapLayer
from datasource import Datasource

class GPSMap(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.map_display = None
        self.vehicle_marker = None
        self.route_layer = None
        self.db_source = None
        self.hazard_markers = {'Severe Potholes': [], 'Slight bumps': []}
        self.max_markers=10

    def build(self):
        self.db_source = Datasource(user_id=1)
        self.map_display = MapView(zoom=12, lat=50.4501, lon=30.5234)
        self.route_layer = LineMapLayer(color=[0, 0, 1, 1])
        self.map_display.add_layer(self.route_layer)

        self.vehicle_marker = MapMarker()
        self.map_display.add_marker(self.vehicle_marker)

        Clock.schedule_interval(self.refresh_data, 1.0)
        self.connection_status_label = Label(
            text="Attempting to connect...",
            font_size='20sp',
            pos_hint={'top': 1, 'x': 0},
            color=[1, 1, 1, 1]
        )
        self.map_display.add_widget(self.connection_status_label)

        return self.map_display

    def on_start(self):
        threading.Thread(target=self._async_connect, daemon=True).start()

    def _async_connect(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.db_source.connect_to_server())
        loop.close()

    def refresh_data(self, *args):
        latest_points = self.db_source.get_new_points()
        if self.db_source.connection_status:
            self.connection_status_label.text = f"Status: {self.db_source.connection_status}"

        for lat, lon, road_condition in latest_points:
            self._update_vehicle_position((lat, lon))
            self.route_layer.add_point((lat, lon))
            if road_condition in self.hazard_markers:
                self._place_hazard_marker(road_condition, (lat, lon))

    def _update_vehicle_position(self, coords):
        self.vehicle_marker.lat, self.vehicle_marker.lon = coords

    def _place_hazard_marker(self, hazard_type, coords):
        if len(self.hazard_markers[hazard_type]) > self.max_markers:
            removed_marker = self.hazard_markers[hazard_type].pop(0)
            self.map_display.remove_marker(removed_marker)
        try:
            marker = MapMarker(lat=coords[0], lon=coords[1], source=f'images/{hazard_type}.png')
            
        except:
            marker = MapMarker(lat=coords[0], lon=coords[1])
        self.map_display.add_marker(marker)
        self.hazard_markers[hazard_type].append(marker)

if __name__ == '__main__':
    GPSMap().run()
