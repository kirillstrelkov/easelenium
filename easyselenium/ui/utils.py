import os
import re
import logging
import traceback

from wx import MessageDialog, OK, CENTER, Notebook, ScrolledWindow, BoxSizer, \
    VERTICAL, StaticBitmap, ALL, EXPAND, Image, BITMAP_TYPE_ANY, BitmapFromImage, \
    Rect, MemoryDC, BufferedDC, BLACK_PEN, TRANSPARENT_BRUSH, GREY_PEN, \
    NullBitmap, EVT_LEFT_DOWN, EVT_MOTION, HORIZONTAL, CallAfter, Dialog, \
    TextCtrl, TE_MULTILINE, TE_READONLY, HSCROLL

from easyselenium.parser.parsed_class import ParsedClass


def get_class_name_from_file(path):
    filename, _ = os.path.splitext(os.path.basename(path))
    return ''.join([w.capitalize() for w in filename.split(u'_')])


def get_py_file_name_from_class_name(class_name):
    words = re.findall('[A-Z]*[a-z0-9]*',
                       class_name)
    words = [w for w in words if len(w) > 0]
    return '_'.join(words).lower() + '.py'


def check_file_for_errors(path, *additional_python_paths):
    syspath = list(os.sys.path)

    for py_path in additional_python_paths:
        if os.path.exists(py_path):
            os.sys.path.append(py_path)

    try:
        ParsedClass.get_parsed_classes(path)
        os.sys.path = syspath
        return True, None
    except Exception:
        os.sys.path = syspath
        formatted_exc = traceback.format_exc()
        return False, formatted_exc


def show_error_dialog(parent, message, caption):
    # TODO: implement dialog correctly - error  message should be easy to read
    return show_dialog(parent, message, caption)


def show_dialog(parent, message, caption, style=OK | CENTER):
    return MessageDialog(parent, message, caption, style).ShowModal()


def show_dialog_path_doesnt_exist(parent, path):
    if path is None:
        path = ''
    msg = u"Path doesn't exist: '%s'" % path
    caption = u'Bad path'
    return show_dialog(parent, msg, caption)


def show_dialog_bad_name(parent, name, *expected_names):
    msg = u"Bad name: '%s'" % name
    if len(expected_names) > 0:
        msg += '\nExpected names like:\n' + u'\n'.join(expected_names)
    caption = u'Bad name'
    return show_dialog(parent, msg, caption)


class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        CallAfter(self.ctrl.AppendText, s)


class Tabs(Notebook):
    def __init__(self, parent, tabs_and_title=None):
        Notebook.__init__(self, parent)
        if tabs_and_title and len(tabs_and_title):
            for tab, title in tabs_and_title:
                self.AddPage(tab(self), title)

    def get_selected_tab_text(self):
        index = self.GetSelection()
        text = self.GetPageText(index)
        return text

    def set_selected_tab_text(self, text):
        index = self.GetSelection()
        self.SetPageText(index, text)


class ImagePanel(ScrolledWindow):
    MIN_SCROLL = 10
    def __init__(self, parent):
        ScrolledWindow.__init__(self, parent)

        self.wx_image = None
        self.original_bitmap = None
        self.greyscaled_bitmap = None
        self.img_path = None

        sizer = BoxSizer(VERTICAL)
        self.static_bitmap = StaticBitmap(self)
        sizer.Add(self.static_bitmap, 1, flag=ALL | EXPAND)

        self.SetSizer(sizer)

    def was_image_loaded(self):
        return (self.img_path and
                self.wx_image and
                self.original_bitmap and
                self.greyscaled_bitmap)

    def get_image_dimensions(self):
        return (self.original_bitmap.GetWidth(),
                self.original_bitmap.GetHeight())

    def load_image(self, path, area=None):
        self.img_path = path
        self.wx_image = Image(path, BITMAP_TYPE_ANY)
        width = self.wx_image.GetWidth()
        height = self.wx_image.GetHeight()
        if area:
            x, y, w, h = area
            bitmap = BitmapFromImage(self.wx_image)
            bitmap_to_draw = bitmap.GetSubBitmap(Rect(x, y, w, h))

            bitmap = bitmap.ConvertToImage()\
            .ConvertToGreyscale(
                0.156, 0.308, 0.060
            ).ConvertToBitmap()

            self.original_bitmap = self._get_bitmap(
                bitmap, bitmap_to_draw, x, y, w, h, False
            )
        else:
            self.original_bitmap = BitmapFromImage(self.wx_image)
        self.greyscaled_bitmap = self.original_bitmap.ConvertToImage().ConvertToGreyscale(
            0.209, 0.411, 0.080
        ).ConvertToBitmap()

        self.static_bitmap.SetBitmap(self.original_bitmap)
        self.SetScrollbars(self.MIN_SCROLL, self.MIN_SCROLL,
                           width / self.MIN_SCROLL, height / self.MIN_SCROLL)

    def _get_bitmap(self, bitmap, bitmap_to_draw, x, y, w, h, draw_frame=True):
        bitmap = bitmap.GetSubBitmap(
            Rect(0,
                 0,
                 bitmap.GetWidth(),
                 bitmap.GetHeight())
        )

        dc = MemoryDC()
        bdc = BufferedDC(dc)
        bdc.SelectObject(bitmap)
        bdc.DrawBitmap(bitmap_to_draw, x, y)

        if draw_frame:
            # Black rect to support white pages
            bdc.SetPen(BLACK_PEN)
            bdc.SetBrush(TRANSPARENT_BRUSH)
            bdc.DrawRectangle(x, y, w, h)

            # Grey rect to support black pages
            bdc.SetPen(GREY_PEN)
            bdc.SetBrush(TRANSPARENT_BRUSH)
            bdc.DrawRectangle(x + 1, y + 1, w - 2, h - 2)

        bdc.SelectObject(NullBitmap)
        return bitmap


class SelectableImagePanel(ImagePanel):
    def __init__(self, parent):
        ImagePanel.__init__(self, parent)
        self.static_bitmap.Bind(EVT_LEFT_DOWN, self.__on_mouse_down)
        self.static_bitmap.Bind(EVT_MOTION, self._on_mouse_move)

        self.__start_position = None
        self.__selected_area = None

    def __on_mouse_down(self, evt):
        self.__start_position = evt.GetPosition()
        if self.was_image_loaded():
            w = self.original_bitmap.GetWidth()
            h = self.original_bitmap.GetHeight()
            self._draw_selected_area((0, 0), (w, h))

    def _on_mouse_move(self, evt):
        if self.was_image_loaded() and evt.Dragging() and self.__start_position:
            # TODO: doesn't work in Windows if window is scrolled
            start_position = self._get_fixed_position(self.__start_position)
            end_position = self._get_fixed_position(evt.GetPosition())
            self._draw_selected_area(start_position, end_position)

    def _get_fixed_position(self, position):
        scroll_offset = (self.GetScrollPos(HORIZONTAL), self.GetScrollPos(VERTICAL))
        return (
            position[0] + scroll_offset[0] * self.MIN_SCROLL,
            position[1] + scroll_offset[1] * self.MIN_SCROLL
        )

    def _draw_selected_area(self, start_pos, end_pos):
        # TODO: reimplement - remove lagging
        x = start_pos[0] if start_pos[0] < end_pos[0] else end_pos[0]
        y = start_pos[1] if start_pos[1] < end_pos[1] else end_pos[1]
        w = abs(end_pos[0] - start_pos[0])
        h = abs(end_pos[1] - start_pos[1])

        self.__selected_area = (x, y, w, h)
        selected_bitmap = self.original_bitmap.GetSubBitmap(Rect(x, y, w, h))
        bitmap = self._get_bitmap(self.greyscaled_bitmap, selected_bitmap, x, y, w, h)
        self.static_bitmap.SetBitmap(bitmap)

    def get_selected_area(self):
        if self.__selected_area:
            return self.__selected_area
        else:
            w, h = self.get_image_dimensions()
            return (0, 0, w, h)


class DialogWithText(Dialog):
    def __init__(self, parent, title):
        Dialog.__init__(self, parent)
        self.SetSizeWH(600, 400)

        sizer = BoxSizer(VERTICAL)

        self.txt_ctrl = TextCtrl(self, style=TE_MULTILINE | TE_READONLY | HSCROLL)
        sizer.Add(self.txt_ctrl, flag=ALL | EXPAND)

        self.SetTitle(title)
