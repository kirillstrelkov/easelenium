import os
import re
from wx import (
    Panel,
    GridBagSizer,
    Button,
    EVT_BUTTON,
    TextCtrl,
    TE_MULTILINE,
    FileDialog,
    FD_SAVE,
    ID_OK,
    BoxSizer,
    VERTICAL,
    TE_READONLY,
    FONTFAMILY_TELETYPE,
    NORMAL,
    CallAfter,
    Font,
    EVT_KEY_DOWN,
    WXK_TAB,
    TextEntryDialog,
    FD_OPEN,
    HSCROLL,
    Dialog,
    StaticText,
    DEFAULT_DIALOG_STYLE,
    RESIZE_BORDER,
    ID_CANCEL,
    ALIGN_RIGHT,
    HORIZONTAL,
)
from wx.grid import EVT_GRID_SELECT_CELL, EVT_GRID_CELL_RIGHT_CLICK

from easyselenium.ui.widgets.utils import (
    show_dialog,
    show_error_dialog,
    show_dialog_bad_name,
)
from easyselenium.ui.utils import (
    FLAG_ALL_AND_EXPAND,
    check_file_for_errors,
    check_py_code_for_errors,
)
from easyselenium.ui.root_folder import RootFolder
from easyselenium.ui.string_utils import StringUtils
from easyselenium.ui.parser.parsed_class import (
    ParsedMouseClass,
    ParsedBrowserClass,
    ParsedPageObjectClass,
)
from easyselenium.ui.file_utils import save_file
from easyselenium.ui.widgets.table import Table
from easyselenium.ui.widgets.utils import Tabs
from easyselenium.utils import is_windows, get_class_name_from_file, LINESEP


class PyFileUI(Panel):
    CHANGED_PREFIX = "*"
    METHOD_TEMPLATE = """
    def {method_name}(self):
        pass

"""

    def __init__(self, parent, file_path, load_file=False):
        Panel.__init__(self, parent)
        self.grandparent = self.GetGrandParent()

        self.__file_path = file_path

        sizer = BoxSizer(VERTICAL)
        self.txt_test_file_path = TextCtrl(
            self, value=self.__file_path, style=TE_READONLY
        )
        sizer.Add(self.txt_test_file_path, 0, flag=FLAG_ALL_AND_EXPAND)

        self.txt_content = TextCtrl(self, style=TE_MULTILINE | HSCROLL)
        self.txt_content.Bind(EVT_KEY_DOWN, self.__on_text_change)
        if load_file:
            self.txt_content.LoadFile(self.__file_path)
        font_size = self.txt_content.GetFont().GetPointSize()
        self.txt_content.SetFont(Font(font_size, FONTFAMILY_TELETYPE, NORMAL, NORMAL))
        sizer.Add(self.txt_content, 1, flag=FLAG_ALL_AND_EXPAND)

        self.SetSizer(sizer)

    def get_file_path(self):
        return self.__file_path

    def __get_selected_tab_text(self):
        parent = self.GetParent()
        return parent.get_tabs_text()

    def __set_selected_tab_text(self, text):
        parent = self.GetParent()
        parent.set_tabs_text(text)

    def load_file(self, path):
        self.__file_path = path
        self.txt_test_file_path.SetValue(self.__file_path)
        self.txt_content.LoadFile(self.__file_path)

    def save_file(self):
        root_folder = self.GetTopLevelParent().get_root_folder()
        text = self.__get_selected_tab_text()
        if text.startswith(self.CHANGED_PREFIX):
            self.__set_selected_tab_text(text[1:])
            save_file(self.__file_path, self.txt_content.GetValue())
            formatted_exc = check_file_for_errors(self.__file_path, root_folder)
            if formatted_exc:
                show_error_dialog(self, formatted_exc, "File contains errors")

    def set_file_was_changed(self):
        text = self.__get_selected_tab_text()
        if not text.startswith(self.CHANGED_PREFIX):
            self.__set_selected_tab_text(self.CHANGED_PREFIX + text)

    def __on_text_change(self, evt):
        key = evt.GetUnicodeKey()
        ctrl_s_pressed = key == 83 and evt.ControlDown()
        if key == WXK_TAB:
            indent = "    "
            self.txt_content.WriteText(indent)
        elif ctrl_s_pressed:
            self.save_file()
        else:
            self.set_file_was_changed()
            evt.Skip()

    def append_text(self, text):
        content = self.txt_content.GetValue()
        pass_with_tab = "    pass"
        if pass_with_tab in content:
            content = content.replace(pass_with_tab, "").rstrip() + LINESEP
            self.txt_content.SetValue(content)

        self.txt_content.AppendText(text)
        self.set_file_was_changed()

    def insert_text(self, line, pos):
        self.txt_content.SetInsertionPoint(pos)
        self.txt_content.WriteText(line.rstrip() + LINESEP)
        self.txt_content.SetInsertionPointEnd()
        self.set_file_was_changed()

    def create_method(self, method_name):
        test_case = self.METHOD_TEMPLATE.format(method_name=method_name)
        self.append_text(test_case)

    def has_one_or_more_methods_or_test_cases(self):
        return len(re.findall("def [a-z_]+\(self.+:", self.txt_content.GetValue())) > 0

    def append_method_call(
        self, field=None, method_name=None, method=None, arg_spec=None
    ):
        # TODO: simplify
        assert field or method_name
        if method_name == "assert":
            var = "expression"
            dialog = MultipleTextEntry(self, "Please enter values", [var])
            if dialog.ShowModal() == ID_OK:
                self.append_text(f"\n        assert {dialog.values[var]}")
            return

        is_po_class_file_selected = type(self) == PyFileUI
        # removing arguments with default value
        args = arg_spec.args
        if arg_spec.defaults:
            args = args[: -len(arg_spec.defaults)]

        # removing 'self' argument
        self_txt = "self"
        if self_txt in args:
            args.remove(self_txt)

        po_class = self.grandparent.get_current_pageobject_class()
        lowered_class_name = po_class.name.lower()

        is_assert_method = method_name.startswith("assert")
        is_browser_method = (
            method_name in ParsedBrowserClass.get_parsed_classes()[0].methods
        )
        is_mouse_method = (
            method_name in ParsedMouseClass.get_parsed_classes()[0].methods
        )
        is_page_object_method = (
            method_name
            in ParsedPageObjectClass.get_parsed_classes(po_class.file_path)[0].methods
        )

        # replacing 'element' with correctly formatted string - self.obj.field
        element_txt = "element"
        if element_txt in args:
            element_index = args.index(element_txt)
            if is_po_class_file_selected:
                args[element_index] = "self.%s" % field.name
            else:
                args[element_index] = "self.%s.%s" % (lowered_class_name, field.name)

        if is_browser_method:
            caller = "self.browser"
        elif is_mouse_method:
            caller = "self.browser.mouse"
        elif is_page_object_method and not is_po_class_file_selected:
            caller = "self." + lowered_class_name
        elif is_assert_method:
            caller = None
        else:
            caller = "self"

        get_prefix = "get_"
        is_getter_method_and_no_args = method_name.startswith(get_prefix)
        method_kwargs = {}
        if is_getter_method_and_no_args:
            var = method_name.replace(get_prefix, "")
            method_call_template = (
                "        {var} = {caller}.{method}({method_args})" + LINESEP
            )
            method_kwargs["var"] = var
        elif caller is None:
            method_call_template = "        {method}({method_args})" + LINESEP
        else:
            method_call_template = "        {caller}.{method}({method_args})" + LINESEP

        if (
            len(args) > 1
            and (is_browser_method or is_mouse_method)
            or len(args) > 0
            and (is_assert_method or is_page_object_method)
        ):
            if is_assert_method or is_page_object_method:
                dialog = MultipleTextEntry(self, "Please enter values", args)
            else:
                dialog = MultipleTextEntry(self, "Please enter values", args[1:])
            if dialog.ShowModal() == ID_OK:
                for name, value in dialog.values.items():
                    args[args.index(name)] = value
                method_kwargs.update(
                    {
                        "caller": caller,
                        "method": method_name,
                        "method_args": ", ".join(args),
                    }
                )
                code_line = method_call_template.format(**method_kwargs)
                code = self.txt_content.GetValue() + LINESEP + code_line
                root_folder = self.GetTopLevelParent().get_root_folder()
                formatted_exception = check_py_code_for_errors(code, root_folder)

                if formatted_exception:
                    show_dialog(
                        self, formatted_exception, "Values are not Python expressions"
                    )
                else:
                    method_kwargs.update(
                        {
                            "caller": caller,
                            "method": method_name,
                            "method_args": ", ".join(args),
                        }
                    )
                    self.append_text(method_call_template.format(**method_kwargs))
        else:
            method_kwargs.update(
                {
                    "caller": caller,
                    "method": method_name,
                    "method_args": ", ".join(args),
                }
            )
            self.append_text(method_call_template.format(**method_kwargs))


class TestFileUI(PyFileUI):
    TEST_FILE_TEMPLATE = """# coding=utf8
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from easyselenium.base_test import BaseTest


class {class_name}(BaseTest):

    @classmethod
    def setUpClass(cls):
        super({class_name}, cls).setUpClass()

    def setUp(self):
        self.browser.get(u'{url}')

"""

    def __init__(self, parent, test_file_path, po_class, load_file=False):
        PyFileUI.__init__(self, parent, test_file_path, load_file)

        self.__po_class = po_class

        if not load_file:
            initial_text = self.TEST_FILE_TEMPLATE.format(
                class_name=get_class_name_from_file(test_file_path), url=po_class.url
            )
            self.txt_content.SetValue(initial_text)

    def __fix_imports(self, po_class):
        root_folder = os.path.normpath(self.GetTopLevelParent().get_root_folder())
        path, _ = os.path.splitext(po_class.file_path)
        path = path.replace(root_folder, "").strip()
        paths = [p for p in os.path.normpath(path).split(os.sep) if len(p) > 0]
        correct_import = ".".join(paths)
        class_name = po_class.name
        import_line = "from {relative_import} import {class_name}".format(
            relative_import=correct_import, class_name=class_name
        )
        text = self.txt_content.GetValue()
        if import_line not in text:
            base_test_import = "import BaseTest"
            shift = 6 if is_windows() else len(LINESEP)  # windows hack
            pos = text.index(base_test_import) + len(base_test_import) + shift
            self.insert_text(import_line, pos)

    def __fix_class_initialization(self, po_class):
        class_name = po_class.name
        field_name = class_name.lower()
        field_line = "        cls.{field_name} = {class_name}(cls.browser, cls.logger)".format(
            field_name=field_name, class_name=class_name
        )

        text = self.txt_content.GetValue()
        if field_line not in text:
            class_def_end = "cls).setUpClass()"
            shift = 13 if is_windows() else len(LINESEP)  # windows hack
            pos = text.index(class_def_end) + len(class_def_end) + shift
            self.insert_text(field_line, pos)

    def append_method_call(
        self, field=None, method_name=None, method=None, arg_spec=None
    ):
        assert field or method_name
        if method_name != "assert":
            po_class = self.grandparent.get_current_pageobject_class()

            self.__fix_class_initialization(po_class)
            self.__fix_imports(po_class)

        PyFileUI.append_method_call(
            self, field=field, method_name=method_name, method=method, arg_spec=arg_spec
        )

    def create_new_test_case(self, test_case_name):
        self.create_method(test_case_name)


class FieldsTableAndTestFilesTabs(Panel):
    TAB_INDEX_FOR_TABLE = 0
    TAB_INDEX_FOR_PO_CLASS_FILE = 1

    def __init__(self, parent, editor_tab):
        Panel.__init__(self, parent)

        self.__editor_tab = editor_tab
        self.__cur_po_class = None

        sizer = GridBagSizer(5, 5)
        full_span = (1, 4)

        row = 0
        inner_sizer = BoxSizer(HORIZONTAL)
        self.btn_open_test_file = Button(self, label="Open test file")
        self.btn_open_test_file.Bind(EVT_BUTTON, self.__on_open_test_file)
        inner_sizer.Add(self.btn_open_test_file)

        self.btn_create_test_file = Button(self, label="Create test file")
        self.btn_create_test_file.Bind(EVT_BUTTON, self.__on_create_test_file)
        inner_sizer.Add(self.btn_create_test_file)

        self.btn_save_test_file = Button(self, label="Save current file")
        self.btn_save_test_file.Bind(EVT_BUTTON, self.__on_save_test_file)
        inner_sizer.Add(self.btn_save_test_file)

        inner_sizer.AddStretchSpacer(1)

        self.btn_create_test = Button(self, label="Create new method/test case")
        self.btn_create_test.Bind(EVT_BUTTON, self.__create_method_or_test)
        inner_sizer.Add(self.btn_create_test)
        sizer.Add(inner_sizer, pos=(row, 0), span=full_span, flag=FLAG_ALL_AND_EXPAND)

        row += 1
        self.tabs = Tabs(self, [(Table, "Fields' table")])
        self.table = self.tabs.GetPage(0)
        self.table.Bind(EVT_GRID_SELECT_CELL, self.__on_cell_click)
        self.table.Bind(EVT_GRID_CELL_RIGHT_CLICK, self.__on_cell_click)

        sizer.Add(self.tabs, pos=(row, 0), span=full_span, flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(1, 1)
        self.SetSizer(sizer)

    def load_po_class(self, po_class):
        self.__cur_po_class = po_class
        self.__set_pageobject_class(self.__cur_po_class)

        file_name = os.path.basename(self.__cur_po_class.file_path)

        more_than_1_tab = self.tabs.GetPageCount() > 1
        if more_than_1_tab:
            py_file_ui = self.tabs.GetPage(self.TAB_INDEX_FOR_PO_CLASS_FILE)
            py_file_ui.load_file(self.__cur_po_class.file_path)
        else:
            py_file_ui = PyFileUI(self.tabs, self.__cur_po_class.file_path, True)
            self.tabs.AddPage(
                py_file_ui, os.path.basename(self.__cur_po_class.file_path)
            )

        if (
            not more_than_1_tab
            and self.tabs.GetSelection() != self.TAB_INDEX_FOR_PO_CLASS_FILE
        ):
            self.tabs.SetSelection(self.TAB_INDEX_FOR_PO_CLASS_FILE)

        self.tabs.set_tabs_text(file_name, self.TAB_INDEX_FOR_PO_CLASS_FILE)

    def get_current_po_class(self):
        return self.__cur_po_class

    def clear_table(self):
        self.table.ClearGrid()

    def get_current_pageobject_class(self):
        return self.__cur_po_class

    def __set_pageobject_class(self, po_class):
        self.__cur_po_class = po_class
        self.table.load_data(po_class.fields)

    def __create_method_or_test(self, evt):
        count = self.tabs.GetPageCount()
        if count > 1:
            page = self.tabs.GetPage(self.tabs.GetSelection())
            if type(page) == PyFileUI:
                self.__create_method(page)
            elif type(page) == TestFileUI:
                self.__create_test(page)
            else:
                show_dialog(
                    self,
                    "Selected tab is not supported"
                    + LINESEP
                    + "Please selected test file or page object class",
                    "Bad selected tab",
                )
        else:
            show_dialog(
                self,
                "Test file was not created." + LINESEP + "Please create a test file.",
                "Test file was not created",
            )

    def __create_method(self, page):
        modal = TextEntryDialog(self, "Enter method name", "Create method")
        if modal.ShowModal() == ID_OK:
            method_name = modal.GetValue()
            if StringUtils.is_method_name_correct(method_name):
                page.create_method(method_name)
            else:
                show_dialog_bad_name(self, method_name, "search", "login", "fill_data")

    def __create_test(self, page):
        modal = TextEntryDialog(self, "Enter test case name", "Create new test case")
        if modal.ShowModal() == ID_OK:
            test_case_name = modal.GetValue()
            if StringUtils.is_test_case_name_correct(test_case_name):
                page.create_new_test_case(test_case_name)
            else:
                show_dialog_bad_name(self, test_case_name, "test_search")

    def __on_save_test_file(self, evt):
        count = self.tabs.GetPageCount()
        if count > 1:
            page = self.tabs.GetPage(self.tabs.GetSelection())
            page.save_file()
        else:
            show_dialog(self, "Please create/open test file.", "Nothing to save")

    def __open_or_create_test_file(self, style):
        if self.__cur_po_class:
            folder = self.GetTopLevelParent().get_root_folder()
            if not folder:
                folder = os.path.dirname(self.__cur_po_class.file_path)
            elif RootFolder.TESTS_FOLDER in os.listdir(folder):
                folder = os.path.join(folder, RootFolder.TESTS_FOLDER)

            dialog = FileDialog(self, defaultDir=folder, style=style, wildcard="*.py")
            if dialog.ShowModal() == ID_OK:
                test_file = dialog.GetPath()
                load_file = style == FD_OPEN

                filename = os.path.basename(test_file)
                if StringUtils.is_test_file_name_correct(test_file):
                    test_file_ui = TestFileUI(
                        self.tabs, test_file, self.__cur_po_class, load_file
                    )
                    self.tabs.AddPage(test_file_ui, filename)
                    self.tabs.SetSelection(self.tabs.GetPageCount() - 1)

                    if style == FD_SAVE:
                        test_file_ui.set_file_was_changed()
                else:
                    show_dialog_bad_name(self, filename, "my_first_test.py")
        else:
            show_dialog(self, "Please select class file.", "Class file was not opened")

    def __on_open_test_file(self, evt):
        self.__open_or_create_test_file(FD_OPEN)

    def __on_create_test_file(self, evt):
        self.__open_or_create_test_file(FD_SAVE)

    def __on_cell_click(self, evt):
        self.table.selected_row = evt.GetRow()
        field = self.table.get_selected_data()
        if field:
            self.__editor_tab.image_panel.draw_selected_field(field, True)
            if evt.GetEventType() == EVT_GRID_CELL_RIGHT_CLICK.typeId and field:
                self.__editor_tab.show_content_menu()
        evt.Skip()


class MultipleTextEntry(Dialog):
    def __init__(self, parent, title, values):
        Dialog.__init__(
            self, parent, title=title, style=DEFAULT_DIALOG_STYLE | RESIZE_BORDER
        )
        self.values = None

        sizer = GridBagSizer(5, 5)
        row = 0
        self.labels = []
        self.txt_ctrls = []
        for value in values:
            label = StaticText(self, label=value)
            self.labels.append(label)
            sizer.Add(label, pos=(row, 0), flag=ALIGN_RIGHT)

            txtctrl = TextCtrl(self)
            self.txt_ctrls.append(txtctrl)
            sizer.Add(txtctrl, pos=(row, 1), flag=FLAG_ALL_AND_EXPAND)
            row += 1

        self.btn_cancel = Button(self, label="Cancel")
        self.btn_cancel.Bind(EVT_BUTTON, self.__on_btn)
        sizer.Add(self.btn_cancel, pos=(row, 0), flag=FLAG_ALL_AND_EXPAND)

        self.btn_ok = Button(self, label="OK")
        self.btn_ok.Bind(EVT_BUTTON, self.__on_btn)
        sizer.Add(self.btn_ok, pos=(row, 1), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(1)
        self.SetSizerAndFit(sizer)
        self.SetSize(400, self.GetSizeTuple()[1])

    def __on_btn(self, evt):
        errors = []
        obj = evt.GetEventObject()
        if obj == self.btn_ok:
            self.values = {}
            for txt_ctrl in self.txt_ctrls:
                label_ctrl = self.labels[self.txt_ctrls.index(txt_ctrl)]
                label = label_ctrl.GetLabel()
                value = txt_ctrl.GetValue()
                self.values[label] = value
                if len(value) == 0:
                    errors.append("Variable '%s' has empty value '%s'" % (label, value))

            return_code = ID_OK
        else:
            self.values = None
            return_code = ID_CANCEL

        if len(errors) > 0:
            show_dialog(self, LINESEP.join(errors), "Bad entered data")
        else:
            CallAfter(self.EndModal, ID_OK)
