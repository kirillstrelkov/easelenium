from easyselenium.ui.context_menu import ContextMenu
from easyselenium.ui.utils import show_dialog


class FieldContextMenu(ContextMenu):
    def __init__(self, field, parsed_classes, test_file, txt_ctrl_ui):
        self.__field = field
        self.__parsed_classes = parsed_classes
        self.__test_file = test_file
        self.__txt_ctrl_ui = txt_ctrl_ui
        data = self.__prepare_data_from_classes(parsed_classes)

        ContextMenu.__init__(self, data)
        self._bind_evt_menu(self.__on_menu_click)

    def __prepare_data_from_classes(self, parsed_classes):
        data = []
        for pc in parsed_classes:
            is_asserts = 'assertTrue' in pc.methods
            is_mouse = 'hover' in pc.methods
            if is_asserts or is_mouse:
                name = u'Mouse' if is_mouse else u'Asserts'
                data.append((name, self.__prepare_context_data(pc.methods)))
                if len(parsed_classes) > 1:
                    data.append((ContextMenu.SEPARATOR_TEXT, None))
            else:
                browser_data = self.__prepare_context_data(pc.methods)
                for name, method in browser_data:
                    data.append((name, method))
        return data

    def __prepare_context_data(self, initial_data):
        if type(initial_data) == dict:
            initial_data = initial_data.items()
        # needs to be initially sorted so that submenu items will be sorted as well
        initial_data = sorted(initial_data, key=lambda x: x[0])

        data = {}
        def append_to_data(submenu_text, item_text, func):
            if submenu_text in data:
                data[submenu_text] += [(item_text, func)]
            else:
                data[submenu_text] = [(item_text, func)]

        for text, func in initial_data:
            if text.startswith('_') or text.startswith('find'):
                continue

            if 'dropdown' in text:
                append_to_data('dropdowns', text, func)
            elif text.startswith('get'):
                append_to_data('getters', text, func)
            elif text.startswith('wait'):
                append_to_data('waits', text, func)
            else:
                data[text] = func

        data = sorted(data.items(), key=lambda x: x[0])
        return data

    def __on_menu_click(self, evt):
        if self.__test_file:
            method = self._get_function(evt.GetId())
            for pc in self.__parsed_classes:
                if method in pc.methods.values():
                    arg_spec = pc.get_arg_spec(method)
                    self.__txt_ctrl_ui.append_method_call(self.__field,
                                                          method,
                                                          arg_spec)
                    break
        else:
            show_dialog(self.GetParent(),
                        u'Please select or create test file.',
                        u'Test file was not selected')
