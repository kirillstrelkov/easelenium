from wx import EVT_LEFT_DOWN, EVT_MOTION, HORIZONTAL, VERTICAL, Rect

from easyselenium.ui.image.image_panel import ImagePanel


class SelectableImagePanel(ImagePanel):
    def __init__(self, parent):
        ImagePanel.__init__(self, parent)
        self.static_bitmap.Bind(EVT_LEFT_DOWN, self.__on_mouse_down)
        self.static_bitmap.Bind(EVT_MOTION, self._on_mouse_move)

        self.__start_position = None
        self.__selected_area = None

    def __on_mouse_down(self, evt):
        self.__start_position = evt.GetPosition()
        if self.was_image_loaded():
            w = self.original_bitmap.GetWidth()
            h = self.original_bitmap.GetHeight()
            self._draw_selected_area((0, 0), (w, h))

    def _on_mouse_move(self, evt):
        if self.was_image_loaded() and evt.Dragging() and self.__start_position:
            # TODO: doesn't work in Windows if window is scrolled
            start_position = self._get_fixed_position(self.__start_position)
            end_position = self._get_fixed_position(evt.GetPosition())
            self._draw_selected_area(start_position, end_position)

    def _get_fixed_position(self, position):
        scroll_offset = (self.GetScrollPos(HORIZONTAL), self.GetScrollPos(VERTICAL))
        return (
            position[0] + scroll_offset[0] * self.MIN_SCROLL,
            position[1] + scroll_offset[1] * self.MIN_SCROLL
        )

    def _draw_selected_area(self, start_pos, end_pos):
        # TODO: reimplement - remove lagging
        x = start_pos[0] if start_pos[0] < end_pos[0] else end_pos[0]
        y = start_pos[1] if start_pos[1] < end_pos[1] else end_pos[1]
        w = abs(end_pos[0] - start_pos[0])
        h = abs(end_pos[1] - start_pos[1])

        self.__selected_area = (x, y, w, h)
        selected_bitmap = self.original_bitmap.GetSubBitmap(Rect(x, y, w, h))
        bitmap = self._get_bitmap(self.greyscaled_bitmap, selected_bitmap, x, y, w, h)
        self.static_bitmap.SetBitmap(bitmap)

    def get_selected_area(self):
        if self.__selected_area:
            return self.__selected_area
        else:
            w, h = self.get_image_dimensions()
            return (0, 0, w, h)