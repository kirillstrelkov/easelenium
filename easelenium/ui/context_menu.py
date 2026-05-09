"""Right click menu."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from wx import EVT_MENU, Event, Menu, MenuItem, NewId

# Each menu item is (label, func_or_submenu) where submenu is a list of the same type
MenuItemData_co = Any  # forward-declared below; use Any to avoid circular alias
MenuData = list[tuple[str, Any]]


class MenuItemData:
    """Data for menu item."""

    def __init__(self, text: str, func: Callable[..., Any]) -> None:
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

    def __init__(self, data: MenuData) -> None:
        """Initialize ContextMenu."""
        Menu.__init__(self)

        self.__id_and_item_data = self.__get_ids_and_item_data(data)
        self.__text_and_item_data = {d.text: d for d in self.__id_and_item_data.values()}

        self.__create_menu(data)
        self._bind_evt_menu(self.__on_menu_click)

    def _bind_evt_menu(self, function: Callable[..., Any]) -> None:
        """Bind event to menu."""
        self.Bind(EVT_MENU, function)
        for menu_item in self.GetMenuItems():
            submenu = menu_item.GetSubMenu()
            if submenu:
                submenu.Bind(EVT_MENU, function)

    def __get_ids_and_item_data(
        self,
        data: MenuData,
    ) -> dict[Any, MenuItemData]:
        """Get ids and item data."""
        _ids_and_data: dict[Any, MenuItemData] = {}
        for text, func in data:
            if type(func) in (list, tuple):
                _ids_and_data.update(self.__get_ids_and_item_data(func))
            item_data = MenuItemData(text, func)
            _ids_and_data[item_data.id] = item_data
        return _ids_and_data

    def __create_menu(self, data: MenuData) -> None:
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
                item_data = self.__text_and_item_data[text]
                item = MenuItem(self, item_data.id, text)
                self.Append(item)

    def _get_menu_item_data(self, menu_item_id: Any) -> MenuItemData | None:  # noqa: ANN401
        """Get menu item data by id."""
        return self.__id_and_item_data.get(menu_item_id)

    def _get_function(self, menu_item_id: Any) -> Callable[..., Any] | None:  # noqa: ANN401
        """Get function from menu item id."""
        menu_item_data = self._get_menu_item_data(menu_item_id)
        return menu_item_data.func if menu_item_data else None

    def __on_menu_click(self, evt: Event) -> None:
        """Handle menu click event."""
        _id = evt.GetId()
        func = self._get_function(_id)
        if func:
            func()
