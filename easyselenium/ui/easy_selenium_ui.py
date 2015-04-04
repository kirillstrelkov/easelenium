from wx import Panel, BoxSizer, VERTICAL, ALL, EXPAND, Frame, App, GridBagSizer, \
    StaticText, TextCtrl, Button, HORIZONTAL, EVT_BUTTON, DirDialog, ID_OK

from easyselenium.ui.editor.editor_ui import EditorTab
from easyselenium.ui.generator_ui import GeneratorTab
from easyselenium.ui.utils import Tabs
from easyselenium.ui.root_folder import RootFolder


class MainFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.SetTitle("Easy Selenium UI")
        self.SetSize((800, 600))

        panel = Panel(self)

        sizer = BoxSizer(VERTICAL)

        hsizer = BoxSizer(HORIZONTAL)
        label = StaticText(panel, label=u'Root folder:')
        hsizer.Add(label)

        self.__txt_root_path = TextCtrl(panel)
        hsizer.Add(self.__txt_root_path, 1, flag=ALL | EXPAND)

        self.btn_set_root = Button(panel, label=u'Set root folder')
        self.btn_set_root.Bind(EVT_BUTTON, self.__set_root_folder)
        hsizer.Add(self.btn_set_root,)
        sizer.Add(hsizer, flag=ALL | EXPAND)

        tabs = Tabs(panel, [(GeneratorTab, "Generator"),
                            (EditorTab, "Editor"),
                            (Panel, "Test runner")])
        sizer.Add(tabs, 1, flag=ALL | EXPAND)

        panel.SetSizer(sizer)
        self.Layout()

    def get_root_folder(self):
        text = self.__txt_root_path.GetValue()
        if text and len(text) > 0:
            return text
        else:
            return None

    def __set_root_folder(self, evt):
        dialog = DirDialog(self)
        if dialog.ShowModal() == ID_OK:
            path = dialog.GetPath()
            RootFolder.prepare_folder(path)
            self.__txt_root_path.SetValue(path)


if __name__ == '__main__':
    app = App(False)
    main_ui = MainFrame(None)
    main_ui.Show()
    app.MainLoop()
