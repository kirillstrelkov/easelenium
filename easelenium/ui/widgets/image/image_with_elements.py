"""UI image with elements."""
from __future__ import annotations

from typing import TYPE_CHECKING

from wx import CURSOR_ARROW, CURSOR_HAND, EVT_MOTION, Cursor, Event, Point, Rect, Window

from easelenium.ui.widgets.image.selectable_image import SelectableImagePanel

if TYPE_CHECKING:
    from easelenium.ui.generator.page_object_class import PageObjectClassField
    from easelenium.ui.utils import TypePoint


class ImageWithElements(SelectableImagePanel):
    """Image with elements."""

    def __init__(self, parent: Window) -> None:
        """Initialize."""
        SelectableImagePanel.__init__(self, parent)
        self.static_bitmap.Bind(EVT_MOTION, self.on_mouse_move)
        self.__po_fields = None
        self.selected_field = None

    def on_mouse_move(self, evt: Event) -> None:
        """Handle mouse move."""
        field = self.get_field(evt.GetPosition())
        if self.selected_field != field:
            self.draw_selected_field(field)
            self.selected_field = field

    def set_po_fields(self, fields: list[PageObjectClassField]) -> None:
        """Set PageObject fields."""
        self.__po_fields = fields

    def draw_selected_field(
        self,
        field: PageObjectClassField,
        *,
        focus: bool = False,
    ) -> None:
        """Draw field on image."""
        end_pos = None
        start_pos = None
        if field:
            end_pos = (
                field.location[0] + field.dimensions[0],
                field.location[1] + field.dimensions[1],
            )
            start_pos = field.location
            cursor = Cursor(CURSOR_HAND)
        else:
            start_pos = (0, 0)
            if self.original_bitmap:
                end_pos = (
                    self.original_bitmap.GetWidth(),
                    self.original_bitmap.GetHeight(),
                )
            cursor = Cursor(CURSOR_ARROW)
        if start_pos and end_pos:
            self._draw_selected_area(start_pos, end_pos)
        self.static_bitmap.SetCursor(cursor)

        if field and focus:
            size = self.GetClientSize()
            x, y = field.location
            w, h = field.dimensions
            scroll_x = (x + w / 2 - size.GetWidth() / 2) / self.MIN_SCROLL
            scroll_y = (y + h / 2 - size.GetHeight() / 2) / self.MIN_SCROLL
            self.Scroll(scroll_x, scroll_y)

    def get_field(self, position: TypePoint) -> PageObjectClassField | None:
        """Return PageObjectClassField based on position from image."""
        position = self._get_fixed_position(position)
        position = Point(*position)
        if self.__po_fields:
            fields_sorted_by_dimensions = sorted(
                self.__po_fields,
                key=lambda f: f.dimensions,
            )
            for field in fields_sorted_by_dimensions:
                field_x, field_y = field.location
                w, h = field.dimensions

                if Rect(field_x, field_y, w, h).Contains(position):
                    return field
            return None

        return None
