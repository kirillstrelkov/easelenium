import os
import re
from threading import Thread

from easelenium.ui.generator.page_object_generator import PageObjectGenerator
from easelenium.ui.root_folder import RootFolder
from easelenium.ui.string_utils import StringUtils
from easelenium.ui.utils import FLAG_ALL_AND_EXPAND
from easelenium.ui.widgets.image.selectable_image import SelectableImagePanel
from easelenium.ui.widgets.utils import (
    DialogWithText,
    WxTextCtrlHandler,
    show_dialog,
    show_dialog_bad_name,
    show_dialog_path_does_exist,
    show_dialog_path_doesnt_exist,
)
from easelenium.utils import LINESEP, Logger, get_py_file_name_from_class_name
from selenium.webdriver.common.by import By
from wx import EVT_BUTTON, EVT_MOTION, Button, GridBagSizer, Panel, StaticText, TextCtrl


class GeneratorTab(Panel):
    def __init__(self, parent):
        Panel.__init__(self, parent)
        self.main_frame = self.GetTopLevelParent()

        self.__create_widgets()

    def __create_widgets(self):
        sizer = GridBagSizer(5, 5)

        row = 0
        col = 0

        # first row
        label = StaticText(self, label=u"Selected area:")
        sizer.Add(label, pos=(row, col))

        col += 1
        self.txt_selected_area = TextCtrl(self, value=u"(0, 0, 0, 0)")
        sizer.Add(self.txt_selected_area, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        label = StaticText(self, label=u"Class name:")
        sizer.Add(label, pos=(row, col))

        col += 1
        self.txt_class_name = TextCtrl(self)
        sizer.Add(self.txt_class_name, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.bth_reload_img = Button(self, label=u"Reload image")
        self.bth_reload_img.Bind(EVT_BUTTON, self.__load_img)
        sizer.Add(self.bth_reload_img, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.btn_generate = Button(self, label=u"Generate")
        self.btn_generate.Bind(EVT_BUTTON, self.generate)
        sizer.Add(self.btn_generate, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        # second row
        row += 1
        col = 0
        self.select_image_panel = SelectableImagePanel(self)
        self.select_image_panel.static_bitmap.Bind(EVT_MOTION, self._on_mouse_move)
        sizer.Add(
            self.select_image_panel,
            pos=(row, col),
            span=(1, 6),
            flag=FLAG_ALL_AND_EXPAND,
        )

        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableRow(row, 1)

        self.SetSizer(sizer)

    def __get_root_folder(self):
        return self.main_frame.get_root_folder()

    def __load_img(self, evt=None):
        browser = self.main_frame.get_browser()
        if browser:
            img_path = browser.save_screenshot(self.main_frame.get_tmp_dir())
            self.select_image_panel.load_image(img_path)

            w, h = self.select_image_panel.get_image_dimensions()

            self.txt_selected_area.SetValue(u"(%d, %d, %d, %d)" % (0, 0, w, h))
            self.main_frame.set_url(browser.get_current_url())

    def _on_mouse_move(self, evt):
        if self.select_image_panel.was_image_loaded():
            SelectableImagePanel.on_mouse_move(self.select_image_panel, evt)
            selected_area = self.select_image_panel.get_selected_area()
            self.txt_selected_area.SetValue(repr(selected_area))

    def __is_gen_data_correct(self):
        root_folder = self.__get_root_folder()
        class_name = self.txt_class_name.GetValue()
        area = self.txt_selected_area.GetValue()
        if not self.main_frame.get_browser():
            msg = "Browser is not opened." + LINESEP + "Please open url."
            caption = "Browser is not opened"
            show_dialog(self, msg, caption)
            return False
        elif not re.match(
            r"\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*\)", area
        ):
            msg = "Selected area is not correct: '%s'" % area
            caption = "Bad selected area"
            show_dialog(self, msg, caption)
            return False
        elif root_folder is None or not os.path.exists(root_folder):
            show_dialog_path_doesnt_exist(self, root_folder)
            return False
        elif len(class_name) == 0:  # if bad class_name
            msg = "Unsupported name for class: '%s'" % class_name
            caption = "Bad name for class"
            show_dialog(self, msg, caption)
            return False
        return True

    def __get_frames(self):
        browser = self.main_frame.get_browser()
        if browser:
            frames = []
            for e in browser.find_elements((By.CSS_SELECTOR, "frame, iframe")):
                name = browser.get_attribute(e, "name")
                src = browser.get_attribute(e, "src")
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
            file_path = os.path.join(
                folder, get_py_file_name_from_class_name(class_name)
            )
            area_as_text = self.txt_selected_area.GetValue()
            url = self.main_frame.get_url()
            if os.path.exists(file_path):
                show_dialog_path_does_exist(self, file_path)
            elif not StringUtils.is_class_name_correct(class_name):
                show_dialog_bad_name(self, class_name, "Header", "ContextMenu")
            elif not StringUtils.is_area_correct(area_as_text):
                show_dialog(
                    self, "Bad selected area: %s" % area_as_text, "Bad selected area"
                )
            elif not StringUtils.is_url_correct(url):
                show_dialog(self, "Bad url: %s" % url, "Bad url")
            else:
                dialog = DialogWithText(self, "Generating page object class...")
                handler = WxTextCtrlHandler(dialog.txt_ctrl)
                logger = Logger(log_to_console=False, handler=handler)

                dialog.Show()

                area = eval(area_as_text)
                generator = PageObjectGenerator(self.main_frame.get_browser(), logger)
                folder_path = self.main_frame.get_tmp_dir()

                def generate():
                    dialog.btn_ok.Disable()
                    po_class = generator.get_po_class_for_url(
                        url, class_name, folder_path, area
                    )
                    po_class.save(folder)
                    logger.info(u"Saving class '%s'..." % po_class.name)
                    logger.info(u"Saved file: %s" % po_class.file_path)
                    logger.info(u"Saved file: %s" % po_class.img_path)
                    logger.info(u"DONE")
                    dialog.btn_ok.Enable()

                thread = Thread(target=generate)
                thread.setDaemon(True)
                thread.start()
