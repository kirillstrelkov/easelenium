"""Editor UI."""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from easelenium.ui.widgets.table import Table

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
    FlexGridSizer,
    GridBagSizer,
    Panel,
    SplitterWindow,
    StaticText,
    Window,
)

from easelenium.ui.editor.field_context_menu import FieldContextMenu
from easelenium.ui.editor.utils import FieldsTableAndTestFilesTabs, PyFileUI, TestFileUI
from easelenium.ui.file_utils import is_correct_python_file, read_file
from easelenium.ui.generator.page_object_class import PageObjectClass, PageObjectClassField
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

        self.__cur_po_class: PageObjectClass | None = None
        self.__create_widgets()

    def __create_widgets(self) -> None:
        """Create widgets."""
        sizer = cast("FlexGridSizer", self.GetSizer())

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
        sizer.Add(inner_sizer, pos=(row, 0), flag=FLAG_ALL_AND_EXPAND)  # type: ignore[arg-type]

        # Next row
        row += 1
        splitter = SplitterWindow(self, style=SP_3D | SP_LIVE_UPDATE)

        self.image_panel = ImageWithElements(splitter)
        self.image_panel.static_bitmap.Bind(EVT_MOTION, self.__on_mouse_move)
        self.image_panel.static_bitmap.Bind(EVT_RIGHT_DOWN, self.__on_right_click)

        self.table_and_test_file_tabs = FieldsTableAndTestFilesTabs(splitter, self)

        splitter.SplitHorizontally(self.image_panel, self.table_and_test_file_tabs)
        sizer.Add(splitter, pos=(row, 0), flag=FLAG_ALL_AND_EXPAND)  # type: ignore[arg-type]

        sizer.AddGrowableRow(row, 1)
        sizer.AddGrowableCol(0, 1)

    def __get_parsed_classes(self, field: PageObjectClassField | None) -> list[ParsedClass]:
        if self.__cur_po_class is None:
            return []
        classes = ParsedPageObjectClass.get_parsed_classes(
            self.__cur_po_class.file_path,
        )
        if len(classes) > 0 and len(classes[0].methods) == 0:
            classes = []
        if field:
            classes += ParsedMouseClass.get_parsed_classes()
            classes += ParsedBrowserClass.get_parsed_classes()
        return classes

    def show_content_menu(self, field: PageObjectClassField | None) -> None:
        """Show content menu."""
        tabs = self.table_and_test_file_tabs.tabs
        count = tabs.GetPageCount()
        if count > 1:
            selected_tab = tabs.GetPage(tabs.GetSelection())
            if type(selected_tab) in (TestFileUI, PyFileUI):
                py_file_ui = cast("PyFileUI", selected_tab)
                file_path = py_file_ui.get_file_path()
                parsed_classes = self.__get_parsed_classes(field)
                field_name = field.name if field is not None else ""
                context_menu = FieldContextMenu(
                    field_name,
                    parsed_classes,
                    file_path,
                    cast("object", py_file_ui),  # type: ignore[arg-type]
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
                cast("Table", self.table_and_test_file_tabs.table),
            )

    def __get_current_field(self, evt: Event) -> PageObjectClassField | None:
        return self.image_panel.get_field(evt.GetPosition())  # type: ignore[attr-defined]

    def __open_class(self, _evt: Event) -> None:
        folder = self.GetTopLevelParent().get_root_folder()  # type: ignore[attr-defined]
        if folder:
            if RootFolder.PO_FOLDER in {p.name for p in Path(folder).iterdir()}:
                folder = (Path(folder) / RootFolder.PO_FOLDER).as_posix()
            dialog = FileDialog(self, defaultDir=folder, wildcard="*.py")
            if dialog.ShowModal() == ID_OK:
                self.__load_po_class(dialog.GetPath())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __load_po_class(self, path: str) -> None:
        cast("Table", self.table_and_test_file_tabs.table).clear_table()

        if not Path(path).exists():
            show_dialog_path_doesnt_exist(self, path)
        if not is_correct_python_file(path):
            show_dialog(self, f"File name is incorrect: {path}", "Bad file name")
        else:
            folder = Path(path).parent
            files = [str(folder / p.name) for p in Path(folder).iterdir() if is_correct_python_file(p.name)]
            self.cb_class_path.Clear()
            self.cb_class_path.AppendItems(files)
            self.cb_class_path.Select(files.index(path))
            try:
                self.__cur_po_class = PageObjectClass.parse_string_to_po_class(
                    read_file(path),
                )
                area = self.__cur_po_class.area
                self.image_panel.set_po_fields(self.__cur_po_class.fields)
                img_path = self.__cur_po_class.img_path
                if img_path is not None:
                    self.image_panel.load_image(img_path, area)

                file_path = self.__cur_po_class.file_path
                if file_path is not None:
                    self.cb_class_path.SetValue(file_path)

                self.table_and_test_file_tabs.load_po_class(self.__cur_po_class)
            except Exception:  # noqa: BLE001
                self.__cur_po_class = None
                show_error_dialog(
                    self,
                    traceback.format_exc(),
                    f"Failed to open file {path}",
                )
