import os
import traceback
from subprocess import check_output

from pytest import main
from wx import (
    Panel,
    GridBagSizer,
    Button,
    TR_SINGLE,
    TR_HAS_BUTTONS,
    SplitterWindow,
    SP_3D,
    SP_LIVE_UPDATE,
    CallAfter,
    TextCtrl,
    VSCROLL,
    TE_MULTILINE,
    TE_READONLY,
    HSCROLL,
    StaticText,
    EVT_BUTTON,
    FileDialog,
    ID_OK,
    FD_OPEN,
    DirDialog,
    DD_DIR_MUST_EXIST,
    FD_FILE_MUST_EXIST,
    FD_MULTIPLE,
    CheckBox,
    EVT_CHECKBOX,
    FD_SAVE,
    FD_OVERWRITE_PROMPT,
    Font,
    FONTFAMILY_TELETYPE,
    NORMAL,
)
from wx import Choice
from wx.lib.agw.customtreectrl import (
    CustomTreeCtrl,
    TR_AUTO_CHECK_CHILD,
    TR_AUTO_CHECK_PARENT,
    EVT_TREE_ITEM_CHECKED,
    TR_AUTO_TOGGLE_CHILD,
)

from easyselenium.browser import Browser
from easyselenium.ui.utils import run_in_separate_thread, FLAG_ALL_AND_EXPAND
from easyselenium.ui.widgets.utils import (
    show_dialog_path_doesnt_exist,
    show_error_dialog,
)
from easyselenium.ui.parser.parsed_class import ParsedClass
from easyselenium.ui.file_utils import get_list_of_files
from easyselenium.ui.root_folder import RootFolder
from easyselenium.base_test import BaseTest
from easyselenium.ui.widgets.utils import DialogWithText
from easyselenium.ui.widgets.utils import InfiniteProgressBarDialog


class RedirectText(object):
    def __init__(self, txt_ctrl):
        self.out = txt_ctrl

    def write(self, string):
        CallAfter(self.out.WriteText, string)

    def isatty(self):
        return False

    def flush(self):
        pass


class TestRunnerTab(Panel):
    def __init__(self, *args, **kwargs):
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
            self.txt_html_report, pos=(row, col), span=(1, 3), flag=FLAG_ALL_AND_EXPAND
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
            self.txt_xml_report, pos=(row, col), span=(1, 3), flag=FLAG_ALL_AND_EXPAND
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
            self.txt_options, pos=(row, col), span=(1, 3), flag=FLAG_ALL_AND_EXPAND
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
            self.btn_load_tests_from_files, pos=(row, col), flag=FLAG_ALL_AND_EXPAND
        )

        col += 1
        self.btn_load_tests_from_dir = Button(self, label="Load tests from directory")
        self.btn_load_tests_from_dir.Bind(EVT_BUTTON, self.__load_tests_from_directory)
        sizer.Add(
            self.btn_load_tests_from_dir, pos=(row, col), flag=FLAG_ALL_AND_EXPAND
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
            window, style=TE_MULTILINE | TE_READONLY | HSCROLL | VSCROLL
        )
        font_size = self.txt_ctrl.GetFont().GetPointSize()
        self.txt_ctrl.SetFont(Font(font_size, FONTFAMILY_TELETYPE, NORMAL, NORMAL))

        window.SplitVertically(self.tree_ctrl, self.txt_ctrl)
        sizer.Add(window, pos=(row, col), span=(1, 5), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableRow(row, 1)
        self.SetSizerAndFit(sizer)

    def __on_show_help(self, evt):
        # TODO: simplify
        text = check_output(
            [
                os.sys.executable,
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__), "../scripts/easyselenium_cli.py"
                    )
                ),
                "--help",
            ]
        )
        DialogWithText(self, "Help for nosetests", text).ShowModal()

    def __on_select_file(self, evt):
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

    def __on_check(self, evt):
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

    def __on_tree_check(self, evt):
        # styles doesn't work: TR_AUTO_CHECK_CHILD | TR_AUTO_CHECK_PARENT | TR_AUTO_TOGGLE_CHILD
        # TODO: fix if all children are check then one child is uncheck - parent is checked
        item = evt.GetItem()
        checked = item.IsChecked()
        parent = item.GetParent()

        def all_children_are_checked(_parent):
            states = [child.IsChecked() for child in _parent.GetChildren()]
            uniq_states = list(set(states))
            return len(uniq_states) == 1 and uniq_states[0] is True

        self.tree_ctrl.AutoCheckChild(item, checked)
        if parent:
            self.tree_ctrl.AutoCheckParent(item, all_children_are_checked(parent))

    def __get_safe_path_from_root_folder(self, subfolder=None):
        folder = self.GetTopLevelParent().get_root_folder()
        if subfolder and folder:
            path_for_subfolder = os.path.join(folder, subfolder)
            if os.path.exists(path_for_subfolder):
                return path_for_subfolder

        return folder if folder else "."

    def __load_tests_to_tree(self, file_paths=None, dir_path=None):
        if file_paths:
            python_files = file_paths
        elif dir_path:
            python_files = [f for f in get_list_of_files(dir_path, True)]
        else:
            python_files = []

        python_files = [
            f
            for f in python_files
            if "test" in os.path.basename(f) and os.path.splitext(f)[-1] == ".py"
        ]
        if len(python_files) > 0:
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
                        root, os.path.abspath(python_file), checkbox_type
                    )

                    parsed_classes = ParsedClass.get_parsed_classes(python_file)
                    for parsed_class in parsed_classes:
                        item = self.tree_ctrl.AppendItem(
                            top_item, parsed_class.name, checkbox_type
                        )

                        test_methods = [
                            k
                            for k in parsed_class.methods.keys()
                            if k.startswith("test_")
                        ]
                        for tc_name in test_methods:
                            self.tree_ctrl.AppendItem(item, tc_name, checkbox_type)

                self.tree_ctrl.ExpandAll()
            except Exception:
                show_error_dialog(self, traceback.format_exc(), "Cannot add test cases")
            finally:
                os.sys.path = syspath

    def __load_tests_from_directory(self, evt):
        folder = self.__get_safe_path_from_root_folder(RootFolder.TESTS_FOLDER)
        if folder:
            dialog = DirDialog(self, defaultPath=folder, style=DD_DIR_MUST_EXIST)
            if dialog.ShowModal() == ID_OK:
                self.__load_tests_to_tree(dir_path=dialog.GetPath())
        else:
            show_dialog_path_doesnt_exist(self, folder)

    def __load_tests_from_files(self, evt):
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

    def __get_command(self):
        root = self.tree_ctrl.GetRootItem()
        tests = []
        for _file in root.GetChildren():
            for _class in _file.GetChildren():
                for test_case in _class.GetChildren():
                    if test_case.IsChecked():
                        # TODO: fix for files that contain spaces
                        test_path = _file.GetText()
                        test_class = _class.GetText()
                        test_method = test_case.GetText()
                        tests.append(f"{test_path}")
                        tests.append(f"-k")
                        tests.append(f"{test_class} and {test_method}")

        if not tests:
            return

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

        nose_cmd = ["easyselenium_cli.py"] + args + tests
        return nose_cmd

    def __run_tests(self, evt):
        # TODO: do not run if root folder is not selected
        self.txt_ctrl.Clear()

        dialog = InfiniteProgressBarDialog(
            self, "Running test cases", "Running selected test cases... Please wait...",
        )

        def wrap_func():
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
                    RootFolder.REPORTS
                )
                BaseTest.FAILED_SCREENSHOT_FOLDER = report_folder

                easyselenium_cmd = " ".join(cmd).replace(
                    "easyselenium_cli.py",
                    "easyselenium_cli.py --browser " + browser_name,
                )
                print(f"Executing command:\n{easyselenium_cmd}")

                main(cmd[1:])
            finally:
                dialog.close_event.set()
                os.sys.stdout = stdout
                os.sys.stderr = stderr

        run_in_separate_thread(wrap_func)
        dialog.ShowModal()
