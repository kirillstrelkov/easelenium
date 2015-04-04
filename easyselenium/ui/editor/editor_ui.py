import os
import traceback

from wx import GridBagSizer, Panel, StaticText, ComboBox, CB_READONLY, ALL, \
    EXPAND, EVT_COMBOBOX, Button, EVT_BUTTON, SplitterWindow, EVT_MOTION, \
    EVT_RIGHT_DOWN, FileDialog, ID_OK

from easyselenium.file_utils import read_file
from easyselenium.generator.page_object_class import PageObjectClass
from easyselenium.parser.parsed_class import ParsedBrowserClass
from easyselenium.ui.editor.image_with_elements import ImageWithElements
from easyselenium.ui.editor.utils import FieldsTableAndTestFilesTabs, \
    FieldContextMenu
from easyselenium.ui.root_folder import RootFolder
from easyselenium.ui.utils import show_dialog, \
    show_dialog_path_doesnt_exist, show_error_dialog


class EditorTab(Panel):
    def __init__(self, parent):
        Panel.__init__(self, parent)
        sizer = GridBagSizer(5, 5)
        self.SetSizer(sizer)

        self.__cur_po_class = None
        self.__create_widgets()

    def __create_widgets(self):
        sizer = self.GetSizer()

        # Next row
        row = 0
        label = StaticText(self, label=u'Class path:')
        sizer.Add(label, pos=(row, 0))

        self.cb_class_path = ComboBox(self, style=CB_READONLY)
        sizer.Add(self.cb_class_path, pos=(row, 1), flag=ALL | EXPAND)
        self.cb_class_path.Bind(EVT_COMBOBOX, self.__on_load_po_class)

        self.btn_reload = Button(self, label=u'Reload')
        self.btn_reload.Bind(EVT_BUTTON, self.__on_load_po_class)
        sizer.Add(self.btn_reload, pos=(row, 2))

        self.btn_open_class = Button(self, label=u'Open class')
        self.btn_open_class.Bind(EVT_BUTTON, self.__open_class)
        sizer.Add(self.btn_open_class, pos=(row, 3))

        # Next row
        row += 1
        splitter = SplitterWindow(self)

        self.image_panel = ImageWithElements(splitter)
        self.image_panel.static_bitmap.Bind(EVT_MOTION, self._on_mouse_move)
        self.image_panel.static_bitmap.Bind(EVT_RIGHT_DOWN, self.__on_right_click)

        self.table_and_test_file_tabs = FieldsTableAndTestFilesTabs(splitter, self)

        splitter.SplitHorizontally(self.image_panel, self.table_and_test_file_tabs)
        sizer.Add(splitter, pos=(row, 0), span=(1, 4), flag=ALL | EXPAND)

        sizer.AddGrowableRow(row, 1)
        sizer.AddGrowableCol(1, 1)

    def _show_content_menu(self, field):
        tabs = self.table_and_test_file_tabs.tabs
        count = tabs.GetPageCount()
        if count > 1:
            test_file_path = tabs.GetPage(tabs.GetSelection()).test_file_path
            txt_ctrl_ui = tabs.GetPage(tabs.GetSelection())
            parsed_browser_class = ParsedBrowserClass.get_parsed_classes()[0]
            context_menu = FieldContextMenu(field,
                                            parsed_browser_class,
                                            test_file_path,
                                            txt_ctrl_ui)
            self.PopupMenu(context_menu)
            context_menu.Destroy()
        else:
            show_dialog(self, u'Please create/open test file.',
                        u'Test file was not created/opened')

    def __on_load_po_class(self, evt):
        path = self.cb_class_path.GetValue()
        if len(path) > 0:
            self.__load_po_class(path)

    def __on_right_click(self, evt):
        field = self.__get_current_field(evt)
        if field:
            self._show_content_menu(field)
        pass

    def _on_mouse_move(self, evt):
        prev_selected_field = self.image_panel.selected_field
        ImageWithElements._on_mouse_move(self.image_panel, evt)
        field = self.image_panel._get_field(evt.GetPosition())
        was_field_changed = field != prev_selected_field
        if (field and self.__cur_po_class and was_field_changed):
            index = self.__cur_po_class.fields.index(field)
            self.table_and_test_file_tabs.select_item_in_table(index)

    def __get_current_field(self, evt):
        return self.image_panel._get_field(evt.GetPosition())

    def __open_class(self, evt):
        folder = self.GetTopLevelParent().get_root_folder()
        if folder:
            if RootFolder.PO_FOLDER in os.listdir(folder):
                folder = os.path.join(folder, RootFolder.PO_FOLDER)
            dialog = FileDialog(self, defaultDir=folder, wildcard=u'*.py')
            if dialog.ShowModal() == ID_OK:
                self.__load_po_class(dialog.GetPath())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __load_po_class(self, path):
        self.table_and_test_file_tabs.clear_table()

        def is_correct_filename(filename):
            name = os.path.basename(filename)
            return name.endswith('.py') and not name.startswith('__')

        if not os.path.exists(path):
            show_dialog_path_doesnt_exist(self, path)
        if not is_correct_filename(path):
            show_dialog(self, u'File name is incorrect: %s' % path,
                        u'Bad file name')
        else:
            folder = os.path.dirname(path)
            files = [os.path.join(folder, p) for p in os.listdir(folder)
                     if is_correct_filename(p)]
            self.cb_class_path.Clear()
            self.cb_class_path.AppendItems(files)
            self.cb_class_path.Select(files.index(path))
            try:
                self.__cur_po_class = PageObjectClass.parse_string_to_po_class(read_file(path))
                area = self.__cur_po_class.area
                self.image_panel.po_class = self.__cur_po_class
                self.image_panel.load_image(self.__cur_po_class.img_path, area)

                self.table_and_test_file_tabs.set_pageobject_class(self.__cur_po_class)

                self.cb_class_path.SetValue(self.__cur_po_class.file_path)
            except Exception:
                self.__cur_po_class = None
                show_error_dialog(self, traceback.format_exc(),
                                  u'Failed to open file %s' % path)
