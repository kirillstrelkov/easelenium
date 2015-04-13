import os
import re
import shutil

from threading import Thread

from tempfile import mkdtemp

from wx import Panel, StaticText, TextCtrl, Button, EXPAND, ALL, \
    EVT_BUTTON, EVT_CLOSE, ComboBox, CB_READONLY, \
    GridBagSizer, EVT_MOTION

from selenium.webdriver.common.by import By

from easyselenium.browser import Browser
from easyselenium.ui.utils import show_dialog, \
    show_dialog_path_doesnt_exist, WxTextCtrlHandler, DialogWithText, LINESEP, \
    show_dialog_bad_name
from easyselenium.ui.root_folder import RootFolder
from easyselenium.ui.string_utils import StringUtils
from easyselenium.utils import Logger
from easyselenium.ui.image.selectable_image import SelectableImagePanel
from easyselenium.ui.generator.page_object_generator import PageObjectGenerator


class GeneratorTab(Panel):
    def __init__(self, parent):
        Panel.__init__(self, parent)
        self.browser = None

        sizer = GridBagSizer(5, 5)
        self.SetSizer(sizer)
        self.__tmp_dir = mkdtemp()
        self.__create_widgets()

        self.GetTopLevelParent().Bind(EVT_CLOSE, self.__on_close)

    def __create_widgets(self):
        sizer = self.GetSizer()

        row = 0
        col = 0
        label = StaticText(self, label=u'Url:')
        sizer.Add(label, pos=(row, col))

        col += 1
        self.txt_url = TextCtrl(self, value=u'https://www.google.com/')  # TODO: remove url
        sizer.Add(self.txt_url, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        label = StaticText(self, label=u'Browser:')
        sizer.Add(label, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        self.cb_browser = ComboBox(self,
                                   style=CB_READONLY,
                                   choices=Browser.get_supported_browsers()[:2][::-1])
        self.cb_browser.Select(0)
        sizer.Add(self.cb_browser, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        self.bth_close_url = Button(self, label=u'Close browser')
        self.bth_close_url.Bind(EVT_BUTTON, self.__close_browser)
        sizer.Add(self.bth_close_url, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        self.bth_open_url = Button(self, label=u'Open url')
        self.bth_open_url.Bind(EVT_BUTTON, self.__open_url)
        sizer.Add(self.bth_open_url, pos=(row, col), flag=ALL | EXPAND)

        # third row
        row += 1
        col = 0
        label = StaticText(self, label=u'Selected area:')
        sizer.Add(label, pos=(row, col))

        col += 1
        self.txt_selected_area = TextCtrl(self, value=u'(0, 0, 0, 0)')
        sizer.Add(self.txt_selected_area, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        label = StaticText(self, label=u'Class name:')
        sizer.Add(label, pos=(row, col))

        col += 1
        self.txt_class_name = TextCtrl(self)
        sizer.Add(self.txt_class_name, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        self.bth_reload_img = Button(self, label=u'Reload image')
        self.bth_reload_img.Bind(EVT_BUTTON, self.__load_img)
        sizer.Add(self.bth_reload_img, pos=(row, col), flag=ALL | EXPAND)

        col += 1
        self.btn_generate = Button(self, label=u'Generate')
        self.btn_generate.Bind(EVT_BUTTON, self.generate)
        sizer.Add(self.btn_generate, pos=(row, col), flag=ALL | EXPAND)

        # third row
        row += 1
        col = 0
        self.select_image_panel = SelectableImagePanel(self)
        self.select_image_panel.static_bitmap.Bind(EVT_MOTION, self._on_mouse_move)
        sizer.Add(self.select_image_panel, pos=(row, col), span=(1, 6), flag=ALL | EXPAND)

        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(row, 1)

    def __get_root_folder(self):
        return self.GetTopLevelParent().get_root_folder()

    def __load_img(self, evt=None):
        if self.browser:
            img_path = self.browser.save_screenshot(self.__tmp_dir)
            self.select_image_panel.load_image(img_path)

            w, h = self.select_image_panel.get_image_dimensions()

            self.txt_selected_area.SetValue(u'(%d, %d, %d, %d)' % (0, 0, w, h))
            self.txt_url.SetValue(self.browser.get_current_url())

    def _on_mouse_move(self, evt):
        if self.select_image_panel.was_image_loaded():
            SelectableImagePanel._on_mouse_move(self.select_image_panel, evt)
            selected_area = self.select_image_panel.get_selected_area()
            self.txt_selected_area.SetValue(repr(selected_area))

    def __is_gen_data_correct(self):
        root_folder = self.__get_root_folder()
        class_name = self.txt_class_name.GetValue()
        area = self.txt_selected_area.GetValue()
        if not self.browser:
            msg = u"Browser is not opened." + LINESEP + "Please open url."
            caption = u'Browser is not opened'
            show_dialog(self, msg, caption)
            return False
        elif not re.match('\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*\)', area):
            msg = u"Selected area is not correct: '%s'" % area
            caption = u'Bad selected area'
            show_dialog(self, msg, caption)
            return False
        elif root_folder is None or not os.path.exists(root_folder):
            show_dialog_path_doesnt_exist(self, root_folder)
            return False
        elif len(class_name) == 0:  # if bad class_name
            msg = u"Unsupported name for class: '%s'" % class_name
            caption = u'Bad name for class'
            show_dialog(self, msg, caption)
            return False
        return True

    def __get_frames(self):
        if self.browser:
            frames = []
            for e in self.browser.find_elements((By.CSS_SELECTOR, 'frame, iframe')):
                name = self.browser.get_attribute(e, 'name')
                src = self.browser.get_attribute(e, 'src')
                frames.append((name, src))
            return frames
        else:
            return None

    def generate(self, evt):
        if self.__is_gen_data_correct():
            folder = self.__get_root_folder()
            if RootFolder.PO_FOLDER in os.listdir(folder):
                folder = os.path.join(folder, RootFolder.PO_FOLDER)

            class_name = self.txt_class_name.GetValue()
            area_as_text = self.txt_selected_area.GetValue()
            url = self.txt_url.GetValue()
            if not StringUtils.is_class_name_correct(class_name):
                show_dialog_bad_name(self, class_name, 'Header', 'ContextMenu')
            elif not StringUtils.is_area_correct(area_as_text):
                show_dialog(self, u'Bad selected area: %s' % area_as_text,
                            u'Bad selected area')
            elif not StringUtils.is_url_correct(url):
                show_dialog(self, u'Bad url: %s' % url, u'Bad url')
            else:
                dialog = DialogWithText(self, 'Generating page object class...')
                handler = WxTextCtrlHandler(dialog.txt_ctrl)
                logger = Logger(log_to_console=False, handler=handler)

                dialog.Show()

                area = eval(area_as_text)
                generator = PageObjectGenerator(self.browser, logger)
                folder_path = self.__tmp_dir

                def generate():
                    dialog.btn_ok.Disable()
                    po_class = generator.get_po_class_for_url(url,
                                                              class_name,
                                                              folder_path,
                                                              area)
                    # TODO: raise modal if file exists
                    po_class.save(folder)
                    logger.info(u"Saving class '%s'..." % po_class.name)
                    logger.info(u'Saved file: %s' % po_class.file_path)
                    logger.info(u'Saved file: %s' % po_class.img_path)
                    logger.info(u'DONE')
                    dialog.btn_ok.Enable()

                thread = Thread(target=generate)
                thread.setDaemon(True)
                thread.start()

    def __open_url(self, evt):
        url = self.txt_url.GetValue()
        if StringUtils.is_url_correct(url):
            name = self.cb_browser.GetValue()
            if self.browser and self.browser.get_browser_initials() != name:
                self.browser.quit()
                self.browser = Browser(name)
            elif not self.browser:
                self.browser = Browser(name)
            self.bth_open_url.Disable()

            self.browser.open(url)
            self.__load_img()

            self.bth_open_url.Enable()
        else:
            show_dialog(self, u'Bad url: %s' % url, u'Bad url')

    def __close_browser(self, evt):
        if self.browser:
            self.browser.quit()
            self.browser = None

    def __on_close(self, evt):
        self.__close_browser(evt)

        shutil.rmtree(self.__tmp_dir)
        self.GetTopLevelParent().Destroy()
