"""Editor UI."""
from __future__ import annotations

import os
import traceback
from pathlib import Path

from wx import (
    ALL,
    CB_READONLY,
    EVT_BUTTON,
    EVT_COMBOBOX,
    EVT_MOTION,
    EVT_RIGHT_DOWN,
    HORIZONTAL,
    ID_OK,
    SP_3D,
    SP_LIVE_UPDATE,
    BoxSizer,
    Button,
    ComboBox,
    Event,
    FileDialog,
    GridBagSizer,
    Panel,
    SplitterWindow,
    StaticText,
    Window,
)

from easelenium.ui.editor.field_context_menu import FieldContextMenu
from easelenium.ui.editor.utils import FieldsTableAndTestFilesTabs, PyFileUI, TestFileUI
from easelenium.ui.file_utils import is_correct_python_file, read_file
from easelenium.ui.generator.page_object_class import PageObjectClass
from easelenium.ui.parser.parsed_class import (
    ParsedBrowserClass,
    ParsedClass,
    ParsedMouseClass,
    ParsedPageObjectClass,
)
from easelenium.ui.root_folder import RootFolder
from easelenium.ui.utils import FLAG_ALL_AND_EXPAND
from easelenium.ui.widgets.image.image_with_elements import ImageWithElements
from easelenium.ui.widgets.utils import (
    ImageAndTableHelper,
    show_dialog,
    show_dialog_path_doesnt_exist,
    show_error_dialog,
)


class EditorTab(Panel):
    """Editor tab."""

    def __init__(self, parent: Window) -> None:
        """Initialize."""
        Panel.__init__(self, parent)
        sizer = GridBagSizer(5, 5)
        self.SetSizer(sizer)

        self.__cur_po_class = None
        self.__create_widgets()

    def __create_widgets(self) -> None:
        """Create widgets."""
        sizer = self.GetSizer()

        # Next row
        inner_sizer = BoxSizer(HORIZONTAL)
        label = StaticText(self, label="Class path:")
        inner_sizer.Add(label, flag=ALL)

        self.cb_class_path = ComboBox(self, style=CB_READONLY)
        self.cb_class_path.Bind(EVT_COMBOBOX, self.__on_load_po_class)
        inner_sizer.Add(self.cb_class_path, 1, flag=FLAG_ALL_AND_EXPAND)

        self.btn_reload = Button(self, label="Reload")
        self.btn_reload.Bind(EVT_BUTTON, self.__on_load_po_class)
        inner_sizer.Add(self.btn_reload, flag=ALL)

        self.btn_open_class = Button(self, label="Open class")
        self.btn_open_class.Bind(EVT_BUTTON, self.__open_class)
        inner_sizer.Add(self.btn_open_class, flag=ALL)

        row = 0
        sizer.Add(inner_sizer, pos=(row, 0), flag=FLAG_ALL_AND_EXPAND)

        # Next row
        row += 1
        splitter = SplitterWindow(self, style=SP_3D | SP_LIVE_UPDATE)

        self.image_panel = ImageWithElements(splitter)
        self.image_panel.static_bitmap.Bind(EVT_MOTION, self.__on_mouse_move)
        self.image_panel.static_bitmap.Bind(EVT_RIGHT_DOWN, self.__on_right_click)

        self.table_and_test_file_tabs = FieldsTableAndTestFilesTabs(splitter, self)

        splitter.SplitHorizontally(self.image_panel, self.table_and_test_file_tabs)
        sizer.Add(splitter, pos=(row, 0), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableRow(row, 1)
        sizer.AddGrowableCol(0, 1)

    def __get_parsed_classes(self, field: str | None) -> list[ParsedClass]:
        classes = ParsedPageObjectClass.get_parsed_classes(
            self.__cur_po_class.file_path,
        )
        if len(classes) > 0 and len(classes[0].methods) == 0:
            classes = []
        if field:
            classes += ParsedMouseClass.get_parsed_classes()
            classes += ParsedBrowserClass.get_parsed_classes()
        return classes

    def show_content_menu(self, field: str | None) -> None:
        """Show content menu."""
        tabs = self.table_and_test_file_tabs.tabs
        count = tabs.GetPageCount()
        if count > 1:
            selected_tab = tabs.GetPage(tabs.GetSelection())
            if type(selected_tab) in (TestFileUI, PyFileUI):
                file_path = selected_tab.get_file_path()
                txt_ctrl_ui = tabs.GetPage(tabs.GetSelection())
                parsed_classes = self.__get_parsed_classes(field)
                context_menu = FieldContextMenu(
                    field,
                    parsed_classes,
                    file_path,
                    txt_ctrl_ui,
                )
                self.PopupMenu(context_menu)
                context_menu.Destroy()
            else:
                show_dialog(
                    self,
                    "Please select tab with test file.",
                    "Tab with test file was not selected",
                )
        else:
            show_dialog(
                self,
                "Please create/open test file.",
                "Test file was not created/opened",
            )

    def __on_load_po_class(self, _evt: Event) -> None:
        path = self.cb_class_path.GetValue()
        if len(path) > 0:
            self.__load_po_class(path)

    def __on_right_click(self, evt: Event) -> None:
        field = self.__get_current_field(evt)
        self.show_content_menu(field)

    def __on_mouse_move(self, evt: Event) -> None:
        if self.__cur_po_class:
            ImageAndTableHelper.select_field_on_mouse_move(
                evt,
                self.__cur_po_class.fields,
                self.image_panel,
                self.table_and_test_file_tabs.table,
            )

    def __get_current_field(self, evt: Event) -> str | None:
        return self.image_panel.get_field(evt.GetPosition())

    def __open_class(self, _evt: Event) -> None:
        folder = self.GetTopLevelParent().get_root_folder()
        if folder:
            if RootFolder.PO_FOLDER in os.listdir(folder):
                folder = (Path(folder) / RootFolder.PO_FOLDER).as_posix()
            dialog = FileDialog(self, defaultDir=folder, wildcard="*.py")
            if dialog.ShowModal() == ID_OK:
                self.__load_po_class(dialog.GetPath())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __load_po_class(self, path: str) -> None:
        self.table_and_test_file_tabs.table.clear_table()

        if not Path(path).exists():
            show_dialog_path_doesnt_exist(self, path)
        if not is_correct_python_file(path):
            show_dialog(self, "File name is incorrect: %s" % path, "Bad file name")
        else:
            folder = Path(path).parent
            files = [
                str(folder / p) for p in os.listdir(folder) if is_correct_python_file(p)
            ]
            self.cb_class_path.Clear()
            self.cb_class_path.AppendItems(files)
            self.cb_class_path.Select(files.index(path))
            try:
                self.__cur_po_class = PageObjectClass.parse_string_to_po_class(
                    read_file(path),
                )
                area = self.__cur_po_class.area
                self.image_panel.set_po_fields(self.__cur_po_class.fields)
                self.image_panel.load_image(self.__cur_po_class.img_path, area)

                self.cb_class_path.SetValue(self.__cur_po_class.file_path)

                self.table_and_test_file_tabs.load_po_class(self.__cur_po_class)
            except Exception:  # noqa: BLE001
                self.__cur_po_class = None
                show_error_dialog(
                    self,
                    traceback.format_exc(),
                    "Failed to open file %s" % path,
                )
