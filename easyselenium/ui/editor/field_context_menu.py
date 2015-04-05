from easyselenium.ui.context_menu import ContextMenu
from easyselenium.ui.utils import show_dialog


class FieldContextMenu(ContextMenu):
    def __init__(self, field, parsed_class, test_file, txt_ctrl_ui):
        self.__field = field
        self.__parsed_class = parsed_class
        self.__test_file = test_file
        self.__txt_ctrl_ui = txt_ctrl_ui
        data = self.__prepare_context_data(self.__parsed_class.methods)

        ContextMenu.__init__(self, data)
        self._bind_evt_menu(self.__on_menu_click)

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

        bad_functions = ('_to_string')
        for text, func in initial_data:
            if text in bad_functions or text.startswith('find'):
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
            args = self.__parsed_class.get_args(method)
            self.__txt_ctrl_ui.append_method_call(self.__field,
                                                  method,
                                                  args)
        else:
            show_dialog(self.GetParent(),
                        u'Please select or create test file.',
                        u'Test file was not selected')