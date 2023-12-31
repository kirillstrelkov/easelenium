"""Right click menu."""
from __future__ import annotations

from typing import Any

from wx import EVT_MENU, Event, Menu, MenuItem, NewId


class MenuItemData:
    """Data for menu item."""

    def __init__(self, text: str, func: callable) -> None:
        """Initialize MenuItemData."""
        self.text = text
        self.func = func
        self.id = NewId()

    def __str__(self) -> str:
        """Return string representation of MenuItemData."""
        return f"MenuItemData({self.__dict__})"

    def __repr__(self) -> str:
        """Return string representation of MenuItemData."""
        return str(self)


class ContextMenu(Menu):
    """Right click menu representation."""

    SEPARATOR_TEXT = "------"

    def __init__(self, data: list[tuple[str, callable]]) -> None:
        """Initialize ContextMenu."""
        Menu.__init__(self)

        self.__id_and_item_data = self.__get_ids_and_item_data(data)
        self.__text_and_item_data = {
            d.text: d for d in self.__id_and_item_data.values()
        }

        self.__create_menu(data)
        self._bind_evt_menu(self.__on_menu_click)

    def _bind_evt_menu(self, function: callable) -> None:
        """Bind event to menu."""
        self.Bind(EVT_MENU, function)
        for menu_item in self.GetMenuItems():
            submenu = menu_item.GetSubMenu()
            if submenu:
                submenu.Bind(EVT_MENU, function)

    def __get_ids_and_item_data(
        self,
        data: list[tuple[str, MenuItemData]],
    ) -> dict[Any, callable]:
        """Get ids and item data."""
        _ids_and_data = {}
        for text, func in data:
            if type(func) in (list, tuple):
                for _id, _item_data in self.__get_ids_and_item_data(func).items():
                    _ids_and_data[_id] = _item_data
            item_data = MenuItemData(text, func)
            _ids_and_data[item_data.id] = item_data
        return _ids_and_data

    def __create_menu(self, data: list[tuple[str, callable]]) -> None:
        """Create menu from data."""
        for text, func in data:
            if type(func) in (list, tuple):
                submenu = Menu()
                for _text, _ in func:
                    _id = self.__text_and_item_data[_text].id
                    sitem = MenuItem(submenu, _id, _text)
                    submenu.Append(sitem)
                self.AppendSubMenu(submenu, text)
            elif text == self.SEPARATOR_TEXT:
                self.AppendSeparator()
            else:
                data = self.__text_and_item_data[text]
                item = MenuItem(self, data.id, text)
                self.Append(item)

    def _get_menu_item_data(self, menu_item_id: Any) -> MenuItemData:  # noqa: ANN401
        return self.__id_and_item_data.get(menu_item_id)

    def _get_function(self, menu_item_id: Any) -> callable:  # noqa: ANN401
        """Get function from menu item id."""
        menu_item_data = self._get_menu_item_data(menu_item_id)
        return menu_item_data.func if menu_item_data else None

    def __on_menu_click(self, evt: Event) -> None:
        """Handle menu click event."""
        _id = evt.GetId()
        func = self._get_function(_id)
        if func:
            func()
