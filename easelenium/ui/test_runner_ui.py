"""Test Runner UI."""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from subprocess import check_output
from typing import Any

import pytest
from wx import (
    DD_DIR_MUST_EXIST,
    EVT_BUTTON,
    EVT_CHECKBOX,
    FD_FILE_MUST_EXIST,
    FD_MULTIPLE,
    FD_OPEN,
    FD_OVERWRITE_PROMPT,
    FD_SAVE,
    FONTFAMILY_TELETYPE,
    HSCROLL,
    ID_OK,
    NORMAL,
    SP_3D,
    SP_LIVE_UPDATE,
    TE_MULTILINE,
    TE_READONLY,
    TR_HAS_BUTTONS,
    TR_SINGLE,
    VSCROLL,
    Button,
    CallAfter,
    CheckBox,
    Choice,
    DirDialog,
    Event,
    FileDialog,
    Font,
    GridBagSizer,
    Panel,
    SplitterWindow,
    StaticText,
    TextCtrl,
    Window,
)
from wx.lib.agw.customtreectrl import (
    EVT_TREE_ITEM_CHECKED,
    TR_AUTO_CHECK_CHILD,
    TR_AUTO_CHECK_PARENT,
    TR_AUTO_TOGGLE_CHILD,
    CustomTreeCtrl,
)

from easelenium.base_test import BaseTest
from easelenium.browser import Browser
from easelenium.ui.file_utils import get_list_of_files
from easelenium.ui.parser.parsed_class import ParsedClass
from easelenium.ui.root_folder import RootFolder
from easelenium.ui.utils import FLAG_ALL_AND_EXPAND, run_in_separate_thread
from easelenium.ui.widgets.utils import (
    DialogWithText,
    InfiniteProgressBarDialog,
    show_dialog_path_doesnt_exist,
    show_error_dialog,
)


class RedirectText:
    """Redirect text to text control."""

    def __init__(self, txt_ctrl: TextCtrl) -> None:
        """Initialize."""
        self.out = txt_ctrl

    def write(self, string: str) -> None:
        """Write string to text control."""
        CallAfter(self.out.WriteText, string)

    def isatty(self) -> bool:
        """Return False."""
        return False

    def flush(self) -> None:
        """Do nothing."""


class TestRunnerTab(Panel):
    """Test Runner Tab."""

    def __init__(  # noqa: PLR0915
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize."""
        Panel.__init__(self, *args, **kwargs)
        sizer = GridBagSizer(5, 5)

        row = 0
        col = 0
        self.cb_html_output = CheckBox(self, label="Report in HTML")
        self.cb_html_output.Bind(EVT_CHECKBOX, self.__on_check)
        sizer.Add(self.cb_html_output, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.txt_html_report = TextCtrl(self, style=TE_READONLY)
        self.txt_html_report.Disable()
        sizer.Add(
            self.txt_html_report,
            pos=(row, col),
            span=(1, 3),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += 3
        self.btn_select_html = Button(self, label="Select HTML file")
        self.btn_select_html.Disable()
        self.btn_select_html.Bind(EVT_BUTTON, self.__on_select_file)
        sizer.Add(self.btn_select_html, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        self.cb_xml_output = CheckBox(self, label="Report in XML")
        self.cb_xml_output.Bind(EVT_CHECKBOX, self.__on_check)
        sizer.Add(self.cb_xml_output, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.txt_xml_report = TextCtrl(self, style=TE_READONLY)
        self.txt_xml_report.Disable()
        sizer.Add(
            self.txt_xml_report,
            pos=(row, col),
            span=(1, 3),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += 3
        self.btn_select_xml = Button(self, label="Select XML file")
        self.btn_select_xml.Disable()
        self.btn_select_xml.Bind(EVT_BUTTON, self.__on_select_file)
        sizer.Add(self.btn_select_xml, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        self.cb_options = CheckBox(self, label="Additional options")
        self.cb_options.Bind(EVT_CHECKBOX, self.__on_check)
        sizer.Add(self.cb_options, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.txt_options = TextCtrl(self)
        self.txt_options.Disable()
        sizer.Add(
            self.txt_options,
            pos=(row, col),
            span=(1, 3),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += 3
        self.btn_nose_help = Button(self, label="Show help")
        self.btn_nose_help.Bind(EVT_BUTTON, self.__on_show_help)
        sizer.Add(self.btn_nose_help, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        self.btn_load_tests_from_files = Button(self, label="Load tests from files")
        self.btn_load_tests_from_files.Bind(EVT_BUTTON, self.__load_tests_from_files)
        sizer.Add(
            self.btn_load_tests_from_files,
            pos=(row, col),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += 1
        self.btn_load_tests_from_dir = Button(self, label="Load tests from directory")
        self.btn_load_tests_from_dir.Bind(EVT_BUTTON, self.__load_tests_from_directory)
        sizer.Add(
            self.btn_load_tests_from_dir,
            pos=(row, col),
            flag=FLAG_ALL_AND_EXPAND,
        )

        col += 1
        dummy_label = StaticText(self)
        sizer.Add(dummy_label, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.cb_browser = Choice(self, choices=Browser.get_supported_browsers())
        self.cb_browser.Select(0)
        sizer.Add(self.cb_browser, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.btn_run = Button(self, label="Run test cases")
        self.btn_run.Bind(EVT_BUTTON, self.__run_tests)
        sizer.Add(self.btn_run, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        row += 1
        col = 0
        window = SplitterWindow(self, style=SP_3D | SP_LIVE_UPDATE)
        self.tree_ctrl = CustomTreeCtrl(
            window,
            style=TR_SINGLE
            | TR_HAS_BUTTONS
            | TR_AUTO_CHECK_CHILD
            | TR_AUTO_CHECK_PARENT
            | TR_AUTO_TOGGLE_CHILD,
        )
        self.tree_ctrl.SetBackgroundColour(self.GetBackgroundColour())
        self.tree_ctrl.SetForegroundColour(self.GetForegroundColour())
        self.tree_ctrl.Bind(EVT_TREE_ITEM_CHECKED, self.__on_tree_check)

        self.txt_ctrl = TextCtrl(
            window,
            style=TE_MULTILINE | TE_READONLY | HSCROLL | VSCROLL,
        )
        font_size = self.txt_ctrl.GetFont().GetPointSize()
        self.txt_ctrl.SetFont(Font(font_size, FONTFAMILY_TELETYPE, NORMAL, NORMAL))

        window.SplitVertically(self.tree_ctrl, self.txt_ctrl)
        sizer.Add(window, pos=(row, col), span=(1, 5), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableRow(row, 1)
        self.SetSizerAndFit(sizer)

    def __on_show_help(self, _evt: Event) -> None:
        # TODO: simplify  # noqa: TD003, FIX002, TD002
        text = check_output(
            [  # noqa: S603
                os.sys.executable,
                str(
                    (Path(__file__).parent / "../scripts/easelenium_cli.py").absolute(),
                ),
                "--help",
            ],
        )
        DialogWithText(self, "Help for nosetests", text).ShowModal()

    def __on_select_file(self, evt: Event) -> None:
        folder = self.__get_safe_path_from_root_folder(RootFolder.REPORTS)
        obj = evt.GetEventObject()
        txt_ctrl = None
        if obj == self.btn_select_html:
            wildcard = "*.html"
            txt_ctrl = self.txt_html_report
        elif obj == self.btn_select_xml:
            wildcard = "*.xml"
            txt_ctrl = self.txt_xml_report
        else:
            wildcard = "*.*"
        dialog = FileDialog(
            self,
            defaultDir=folder,
            style=FD_SAVE | FD_OVERWRITE_PROMPT,
            wildcard=wildcard,
        )
        if dialog.ShowModal() == ID_OK and txt_ctrl:
            txt_ctrl.SetValue(dialog.GetPath())

    def __on_check(self, evt: Event) -> Event:
        cb_obj = evt.GetEventObject()
        checkboxes_and_txt_ctrls = {
            self.cb_html_output: self.txt_html_report,
            self.cb_options: self.txt_options,
            self.cb_xml_output: self.txt_xml_report,
        }
        checkboxes_and_btns = {
            self.cb_html_output: self.btn_select_html,
            self.cb_xml_output: self.btn_select_xml,
        }
        txt_ctrl = checkboxes_and_txt_ctrls[cb_obj]
        btn = checkboxes_and_btns.get(cb_obj)
        if txt_ctrl.IsEnabled():
            txt_ctrl.Disable()
            if btn:
                btn.Disable()
        else:
            txt_ctrl.Enable()
            if btn:
                btn.Enable()

    def __on_tree_check(self, evt: Event) -> None:
        # styles doesn't work:
        # TR_AUTO_CHECK_CHILD | TR_AUTO_CHECK_PARENT | TR_AUTO_TOGGLE_CHILD
        # TODO: fix if all children are checked  # noqa: FIX002, TD002, TD003
        # then one child is unchecked - parent is checked
        item = evt.GetItem()
        checked = item.IsChecked()
        parent = item.GetParent()

        def all_children_are_checked(_parent: Window) -> bool:
            states = [child.IsChecked() for child in _parent.GetChildren()]
            uniq_states = list(set(states))
            return len(uniq_states) == 1 and uniq_states[0] is True

        self.tree_ctrl.AutoCheckChild(item, checked)
        if parent:
            self.tree_ctrl.AutoCheckParent(item, all_children_are_checked(parent))

    def __get_safe_path_from_root_folder(self, subfolder: str | None = None) -> str:
        folder = self.GetTopLevelParent().get_root_folder()
        if subfolder and folder:
            path_for_subfolder = Path(folder) / subfolder
            if path_for_subfolder.exists():
                return str(path_for_subfolder)

        return folder if folder else "."

    def __load_tests_to_tree(
        self,
        file_paths: list[str] | None = None,
        dir_path: str | None = None,
    ) -> None:
        if file_paths:
            python_files = file_paths
        elif dir_path:
            python_files = get_list_of_files(dir_path, recursively=True)
        else:
            python_files = []

        python_files = [
            f
            for f in python_files
            if "test" in Path(f).name and Path(f).suffix == ".py"
        ]
        if python_files:
            syspath = list(os.sys.path)
            try:
                root_folder = self.__get_safe_path_from_root_folder()

                if root_folder not in os.sys.path:
                    os.sys.path.append(root_folder)

                checkbox_type = 1
                self.tree_ctrl.DeleteAllItems()
                root = self.tree_ctrl.AddRoot("All test cases", checkbox_type)

                for python_file in python_files:
                    top_item = self.tree_ctrl.AppendItem(
                        root,
                        str(Path(python_file).absolute()),
                        checkbox_type,
                    )

                    parsed_classes = ParsedClass.get_parsed_classes(python_file)
                    for parsed_class in parsed_classes:
                        item = self.tree_ctrl.AppendItem(
                            top_item,
                            parsed_class.name,
                            checkbox_type,
                        )

                        test_methods = [
                            k for k in parsed_class.methods if k.startswith("test_")
                        ]
                        for tc_name in test_methods:
                            self.tree_ctrl.AppendItem(item, tc_name, checkbox_type)

                self.tree_ctrl.ExpandAll()
            except Exception:  # noqa: BLE001
                show_error_dialog(self, traceback.format_exc(), "Cannot add test cases")
            finally:
                os.sys.path = syspath

    def __load_tests_from_directory(self, _evt: Event) -> None:
        folder = self.__get_safe_path_from_root_folder(RootFolder.TESTS_FOLDER)
        if folder:
            dialog = DirDialog(self, defaultPath=folder, style=DD_DIR_MUST_EXIST)
            if dialog.ShowModal() == ID_OK:
                self.__load_tests_to_tree(dir_path=dialog.GetPath())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __load_tests_from_files(self, _evt: Event) -> None:
        folder = self.__get_safe_path_from_root_folder(RootFolder.TESTS_FOLDER)
        if folder:
            dialog = FileDialog(
                self,
                defaultDir=folder,
                style=FD_OPEN | FD_FILE_MUST_EXIST | FD_MULTIPLE,
                wildcard="*.py",
            )
            if dialog.ShowModal() == ID_OK:
                self.__load_tests_to_tree(file_paths=dialog.GetPaths())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __get_command(self) -> None:
        root = self.tree_ctrl.GetRootItem()
        tests = []
        for _file in root.GetChildren():
            for _class in _file.GetChildren():
                for test_case in _class.GetChildren():
                    if test_case.IsChecked():
                        # TODO: fix for files that contain spaces  # noqa: TD002, TD003, FIX002, E501
                        test_path = _file.GetText()
                        test_class = _class.GetText()
                        test_method = test_case.GetText()
                        tests.append(f"{test_path}")
                        tests.append("-k")
                        tests.append(f"{test_class} and {test_method}")

        if not tests:
            return None

        args = [
            f"--rootdir={self.__get_safe_path_from_root_folder()}",
        ]

        use_html_report = (
            self.cb_html_output.IsChecked() and len(self.txt_html_report.GetValue()) > 0
        )
        if use_html_report:
            report_path = self.txt_html_report.GetValue()
            args.append(f"--html={report_path}")

        use_xml_report = (
            self.cb_xml_output.IsChecked() and len(self.txt_xml_report.GetValue()) > 0
        )
        if use_xml_report:
            report_path = self.txt_xml_report.GetValue()
            args.append(f"--junitxml={report_path}")

        use_options = (
            self.cb_options.IsChecked() and len(self.txt_options.GetValue()) > 0
        )
        if use_options:
            report_path = self.txt_options.GetValue()
            args.append(report_path)

        return ["easelenium_cli.py", *args, *tests]

    def __run_tests(self, _evt: Event) -> None:
        # TODO: do not run if root folder is not selected  # noqa: TD002, FIX002, TD003
        self.txt_ctrl.Clear()

        dialog = InfiniteProgressBarDialog(
            self,
            "Running test cases",
            "Running selected test cases... Please wait...",
        )

        def wrap_func() -> None:
            stdout = os.sys.stdout
            stderr = os.sys.stderr
            redirected = RedirectText(self.txt_ctrl)
            os.sys.stdout = redirected
            os.sys.stderr = redirected
            try:
                cmd = self.__get_command()
                browser_name = self.cb_browser.GetStringSelection()
                Browser.DEFAULT_BROWSER = browser_name
                report_folder = self.__get_safe_path_from_root_folder(
                    RootFolder.REPORTS,
                )
                BaseTest.FAILED_SCREENSHOT_FOLDER = report_folder

                easelenium_cmd = " ".join(cmd).replace(
                    "easelenium_cli.py",
                    "easelenium_cli.py --browser " + browser_name,
                )
                print(f"Executing command:\n{easelenium_cmd}")  # noqa: T201

                pytest.main(cmd[1:])
            finally:
                dialog.close_event.set()
                os.sys.stdout = stdout
                os.sys.stderr = stderr

        run_in_separate_thread(wrap_func)
        dialog.ShowModal()
