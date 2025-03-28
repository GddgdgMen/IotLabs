# from math import radians, log, tan, cos, pi

# from kivy.graphics import Color, Ellipse, PushMatrix, Translate, Scale, PopMatrix

# from MapView.libs.garden.garden_mapview.mapview import *
# from MapView.libs.garden.garden_mapview.mapview import MIN_LONGITUDE, MAX_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE
# from MapView.libs.garden.garden_mapview.mapview.utils import clamp


# class AirQualityMapLayer(MapLayer):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.zoom = 0
#         self.points = []

#     def add_point(self, point):
#         self.points.append(point)
#         self.clear_and_redraw()  # Redraw whenever a point is added

#     def get_x(self, lon):
#         """Get the x position on the map using this map source's projection
#         (0, 0) is located at the top left.
#         """
#         return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE) * self.ms / 360.0

#     def get_y(self, lat):
#         """Get the y position on the map using this map source's projection
#         (0, 0) is located at the top left.
#         """
#         lat = radians(clamp(-lat, MIN_LATITUDE, MAX_LATITUDE))
#         return (1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi) * self.ms / 2.0

#     def reposition(self):
#         map_view = self.parent
#         if self.zoom != map_view.zoom:
#             self.ms = pow(2.0, map_view.zoom) * map_view.map_source.dp_tile_size
#             self.clear_and_redraw()

#     def clear_and_redraw(self, *args):
#         with self.canvas:
#             # Clear old circles
#             self.canvas.clear()
#         self._draw_circles()

#     def _draw_circles(self, *args):
#         if not self.points:
#             return
#         map_view = self.parent
#         self.zoom = map_view.zoom
#         # Get the scatter transform (applied to the map tiles)
#         scatter = map_view._scatter
#         sx, sy, ss = scatter.x, scatter.y, scatter.scale


#         # The radius of the circle we'll draw (adjust as needed)
#         radius = 5 * map_view.scale

#         with self.canvas:
#             PushMatrix()
#             # Offset by the MapView's position in the window (should be 0,0)
#             Translate(*map_view.pos)
#             # Undo the scatter animation transform
#             Scale(1 / ss, 1 / ss, 1)
#             Translate(-sx, -sy)

#             for lat, lon, _, air_quality_status in self.points:  # Extract status
#                 # Get the pixel coordinates of the point
#                 x = self.get_x(lon) * ss + sx - radius
#                 y = self.get_y(lat) * ss + sy - radius
#                 x, y = map_view.to_widget(x, y)  # Convert to widget coordinates

#                 # Determine color based on air quality status
#                 if air_quality_status == "Good":
#                     color = (0, 1, 0, 0.5)  # Green
#                 elif air_quality_status == "Moderate":
#                     color = (1, 1, 0, 0.5)  # Yellow
#                 elif air_quality_status == "Unhealthy for Sensitive Groups":
#                     color = (1, 0.5, 0, 0.5)  # Orange
#                 elif air_quality_status == "Unhealthy":
#                     color = (1, 0, 0, 0.5)  # Red
#                 elif air_quality_status == "Very Unhealthy":
#                     color = (0.5, 0, 0.5, 0.5)  # Purple
#                 else:  # Hazardous or unknown
#                     color = (0.5, 0, 0, 0.5)  # Dark red

#                 Color(*color)
#                 Ellipse(pos=(x - radius, y - radius), size=(2 * radius, 2 * radius))
#             PopMatrix()