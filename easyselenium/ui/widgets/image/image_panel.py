from wx import ScrolledWindow, BoxSizer, VERTICAL, StaticBitmap, Image, BITMAP_TYPE_ANY, Bitmap, Rect, \
    MemoryDC, BufferedDC, \
    BLACK_PEN, TRANSPARENT_BRUSH, GREY_PEN, NullBitmap

from easyselenium.ui.utils import FLAG_ALL_AND_EXPAND


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
        sizer.Add(self.static_bitmap, 1, flag=FLAG_ALL_AND_EXPAND)

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
        self.Scroll(0, 0)
        self.img_path = path
        self.wx_image = Image(path, BITMAP_TYPE_ANY)
        width = self.wx_image.GetWidth()
        height = self.wx_image.GetHeight()
        if area:
            x, y, w, h = area
            bitmap = Bitmap(self.wx_image)
            bitmap_to_draw = bitmap.GetSubBitmap(Rect(x, y, w, h))

            bitmap = bitmap.ConvertToImage().ConvertToGreyscale(
                0.156, 0.308, 0.060
            ).ConvertToBitmap()

            self.original_bitmap = self._get_bitmap(
                bitmap, bitmap_to_draw, x, y, w, h, False
            )
        else:
            self.original_bitmap = Bitmap(self.wx_image)
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
