from threading import Thread
from wx import Panel, GridBagSizer, Button, EVT_BUTTON, \
    EVT_MOTION, SplitterWindow, SP_3D, SP_LIVE_UPDATE
from wx.grid import EVT_GRID_SELECT_CELL

from easyselenium.ui.utils import FLAG_ALL_AND_EXPAND
from easyselenium.ui.widgets.utils import show_dialog
from easyselenium.ui.string_utils import StringUtils
from easyselenium.ui.widgets.image.image_with_elements import ImageWithElements
from easyselenium.ui.widgets.table import Table
from easyselenium.ui.widgets.utils import ImageAndTableHelper
from easyselenium.ui.widgets.utils import DialogWithText
from easyselenium.ui.widgets.utils import WxTextCtrlHandler
from easyselenium.utils import Logger
from easyselenium.ui.generator.page_object_generator import PageObjectGenerator


class SelectorFinderTab(Panel):
    def __init__(self, parent):
        Panel.__init__(self, parent)

        self.main_frame = self.GetTopLevelParent()
        self.po_fields = None

        self.__create_widgets()

    def __create_widgets(self):
        sizer = GridBagSizer(5, 5)

        row = 0
        col = 1
        self.bth_reload_img = Button(self, label=u'Reload image')
        self.bth_reload_img.Bind(EVT_BUTTON, self.__load_img)
        sizer.Add(self.bth_reload_img, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)

        col += 1
        self.bth_reload_selectors = Button(self, label=u'Find selectors')
        self.bth_reload_selectors.Bind(EVT_BUTTON, self.__find_selectors)
        sizer.Add(self.bth_reload_selectors, pos=(row, col), flag=FLAG_ALL_AND_EXPAND)
        # third row
        row += 1
        col = 0

        splitter = SplitterWindow(self, style=SP_3D | SP_LIVE_UPDATE)

        self.image_panel = ImageWithElements(splitter)
        self.image_panel.static_bitmap.Bind(EVT_MOTION, self.__on_mouse_move)

        self.table = Table(splitter)
        self.table.Bind(EVT_GRID_SELECT_CELL, self.__on_cell_select)

        splitter.SplitHorizontally(self.image_panel, self.table)
        sizer.Add(splitter, pos=(row, col), span=(1, 3), flag=FLAG_ALL_AND_EXPAND)

        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableRow(row, 1)

        self.SetSizer(sizer)

    def __update_table(self):
        if self.po_fields:
            self.table.load_data(self.po_fields)

    def __on_mouse_move(self, evt):
        ImageAndTableHelper.select_field_on_mouse_move(
            evt,
            self.po_fields,
            self.image_panel,
            self.table
        )

    def __on_cell_select(self, evt):
        self.table.selected_row = evt.GetRow()
        self.image_panel.draw_selected_field(self.table.get_selected_data(), True)
        evt.Skip()

    def __load_img(self, evt=None):
        browser = self.main_frame.get_browser()
        if browser:
            img_path = browser.save_screenshot(self.main_frame.get_tmp_dir())
            self.image_panel.load_image(img_path)
            self.main_frame.set_url(browser.get_current_url())

    def __find_selectors(self, evt):
        browser = self.main_frame.get_browser()
        if browser:
            url = self.main_frame.get_url()
            if not StringUtils.is_url_correct(url):
                show_dialog(self, u'Bad url: %s' % url, u'Bad url')
            else:
                dialog = DialogWithText(self, 'Finding selectors...')
                handler = WxTextCtrlHandler(dialog.txt_ctrl)
                logger = Logger(log_to_console=False, handler=handler)

                dialog.Show()

                generator = PageObjectGenerator(browser, logger)

                def find_selectors():
                    dialog.btn_ok.Disable()
                    self.po_fields = generator.get_all_po_fields(url, None)
                    logger.info(u'DONE')
                    self.__update_table()
                    dialog.btn_ok.Enable()

                thread = Thread(target=find_selectors)
                thread.setDaemon(True)
                thread.start()
