"""Selectable image panel."""
from wx import EVT_LEFT_DOWN, EVT_MOTION, HORIZONTAL, VERTICAL, Event, Rect, Window

from easelenium.ui.utils import TypeArea, TypePoint
from easelenium.ui.widgets.image.image_panel import ImagePanel
from easelenium.utils import is_windows


class SelectableImagePanel(ImagePanel):
    """Selectable image panel."""

    def __init__(self, parent: Window) -> None:
        """Initialize."""
        ImagePanel.__init__(self, parent)
        self.static_bitmap.Bind(EVT_LEFT_DOWN, self.__on_mouse_down)
        self.static_bitmap.Bind(EVT_MOTION, self.on_mouse_move)

        self.__start_position = None
        self.__selected_area = None

    def __on_mouse_down(self, evt: Event) -> None:
        self.__start_position = evt.GetPosition()
        if self.was_image_loaded():
            w = self.original_bitmap.GetWidth()
            h = self.original_bitmap.GetHeight()
            self._draw_selected_area((0, 0), (w, h))

    def on_mouse_move(self, evt: Event) -> None:
        """Handle mouse move."""
        if self.was_image_loaded() and evt.Dragging() and self.__start_position:
            # TODO: doesn't work in Windows if window is scrolled  # noqa: TD002, TD003, FIX002, E501
            start_position = self._get_fixed_position(self.__start_position)
            end_position = self._get_fixed_position(evt.GetPosition())
            self._draw_selected_area(start_position, end_position)

    def _get_fixed_position(self, position: TypePoint) -> TypePoint:
        fix_for_scrolling = 0 if is_windows() else self.MIN_SCROLL
        scroll_offset = (self.GetScrollPos(HORIZONTAL), self.GetScrollPos(VERTICAL))
        return (
            position[0] + scroll_offset[0] * fix_for_scrolling,
            position[1] + scroll_offset[1] * fix_for_scrolling,
        )

    def _draw_selected_area(self, start_pos: int, end_pos: int) -> None:
        # TODO: reimplement - remove lagging  # noqa: TD002, FIX002, TD003
        x = start_pos[0] if start_pos[0] < end_pos[0] else end_pos[0]
        y = start_pos[1] if start_pos[1] < end_pos[1] else end_pos[1]
        w = abs(end_pos[0] - start_pos[0])
        h = abs(end_pos[1] - start_pos[1])

        self.__selected_area = (x, y, w, h)
        selected_bitmap = self.original_bitmap.GetSubBitmap(Rect(x, y, w, h))
        bitmap = self._get_bitmap(self.greyscaled_bitmap, selected_bitmap, x, y, w, h)
        self.static_bitmap.SetBitmap(bitmap)

    def get_selected_area(self) -> TypeArea:
        """Get selected area."""
        if self.__selected_area:
            return self.__selected_area

        w, h = self.get_image_dimensions()
        return 0, 0, w, h
