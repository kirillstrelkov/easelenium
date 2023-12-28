from wx import EVT_MENU, Menu, MenuItem, NewId


class MenuItemData:
    def __init__(self, text, func):
        self.text = text
        self.func = func
        self.id = NewId()

    def __str__(self):
        return f"MenuItemData({self.__dict__})"

    def __repr__(self):
        return str(self)


class ContextMenu(Menu):
    SEPARATOR_TEXT = "------"

    def __init__(self, data):
        Menu.__init__(self)

        self.__id_and_item_data = self.__get_ids_and_item_data(data)
        self.__text_and_item_data = dict(
            [(d.text, d) for d in self.__id_and_item_data.values()],
        )

        self.__create_menu(data)
        self._bind_evt_menu(self.__on_menu_click)

    def _bind_evt_menu(self, function):
        self.Bind(EVT_MENU, function)
        for menu_item in self.GetMenuItems():
            submenu = menu_item.GetSubMenu()
            if submenu:
                submenu.Bind(EVT_MENU, function)

    def __get_ids_and_item_data(self, data):
        _ids_and_data = dict()
        for text, func in data:
            if type(func) in (list, tuple):
                for _id, _item_data in self.__get_ids_and_item_data(func).items():
                    _ids_and_data[_id] = _item_data
            item_data = MenuItemData(text, func)
            _ids_and_data[item_data.id] = item_data
        return _ids_and_data

    def __create_menu(self, data):
        for text, func in data:
            if type(func) in (list, tuple):
                submenu = Menu()
                for _text, _ in func:
                    _id = self.__text_and_item_data[_text].id
                    sitem = MenuItem(submenu, _id, _text)
                    submenu.Append(sitem)
                self.AppendSubMenu(submenu, text)
            else:
                if text == self.SEPARATOR_TEXT:
                    self.AppendSeparator()
                else:
                    data = self.__text_and_item_data[text]
                    item = MenuItem(self, data.id, text)
                    self.Append(item)

    def _get_menu_item_data(self, menu_item_id):
        return self.__id_and_item_data.get(menu_item_id)

    def _get_function(self, menu_item_id):
        menu_item_data = self._get_menu_item_data(menu_item_id)
        return menu_item_data.func if menu_item_data else None

    def __on_menu_click(self, evt):
        _id = evt.GetId()
        func = self._get_function(_id)
        if func:
            func()
