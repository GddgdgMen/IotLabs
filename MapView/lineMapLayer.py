from kivy_garden.mapview import MapLayer
from kivy.graphics import Color, Line, PushMatrix, PopMatrix, Translate, Scale
from math import radians, log, tan, cos, pi
from kivy_garden.mapview.utils import clamp

class LineMapLayer(MapLayer):
    def __init__(self, color=[0, 0, 1, 1], width=2, **kwargs):
        super().__init__(**kwargs)
        self.path_coords = []
        self.color = color
        self._width = width
        self.zoom = self.lon = self.lat = self.ms = 0
        self._computed_points = None
        self._offset = (0, 0)

    def add_point(self, coords):
        self.path_coords.append(coords)
        self._invalidate_cache()
        self._redraw()

    def _invalidate_cache(self):
        self._computed_points = None
        self._offset = (0, 0)

    def _recompute_points(self):
        self._offset = (self._x_offset(self.path_coords[0][1]), self._y_offset(self.path_coords[0][0]))
        self._computed_points = [(self._x_offset(lon) - self._offset[0], self._y_offset(lat) - self._offset[1])
                                 for lat, lon in self.path_coords]

    def _x_offset(self, lon):
        return clamp(lon, -180, 180) * self.ms / 360.0

    def _y_offset(self, lat):
        lat = radians(clamp(-lat, -85, 85))
        return (1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi) * self.ms / 2.0

    def reposition(self):
        if not self.parent:
            return
        view = self.parent
        if self.zoom != view.zoom or self.lon != round(view.lon, 7) or self.lat != round(view.lat, 7):
            self.ms = pow(2.0, view.zoom) * view.map_source.dp_tile_size
            self._invalidate_cache()
            self._redraw()

    def _redraw(self):
        if not self.path_coords:
            return
        self._recompute_points()
        with self.canvas:
            self.canvas.clear()
            PushMatrix()
            view = self.parent
            Translate(*view.pos)
            Scale(1 / view._scatter.scale, 1 / view._scatter.scale, 1)
            Translate(-view._scatter.x, -view._scatter.y)
            Scale(view.scale, view.scale, 1)
            Translate(-view.viewport_pos[0], -view.viewport_pos[1])
            Translate(self.ms / 2, 0)
            Translate(*self._offset)
            Color(*self.color)
            Line(points=self._computed_points, width=self._width)
            PopMatrix()
