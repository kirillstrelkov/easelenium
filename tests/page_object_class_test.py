"""Page object class tests."""
from __future__ import annotations

import codecs
import pickle
from pathlib import Path
from unittest.case import TestCase

from selenium.webdriver.common.by import By

from easelenium.ui.file_utils import check_if_path_exists, read_file, safe_remove_path
from easelenium.ui.generator.page_object_class import (
    PageObjectClass,
    get_by_as_code_str,
    get_by_from_code_str,
)
from easelenium.utils import is_windows


class PageObjectClassTest(TestCase):
    """PageObjectClass tests."""

    @classmethod
    def setUpClass(cls: type[PageObjectClassTest]) -> None:
        """Set up class."""
        super().setUpClass()
        cur_path = Path(__file__).parent
        cls.pickled_object_path = str(cur_path / "data" / "pickled_po_class_object")
        cls.expected_duckduckgo_class_path = str(
            cur_path / "data" / "expected_duckduckgo_class_py",
        )
        cls.po_class_object = pickle.load(  # noqa: S301
            codecs.open(cls.pickled_object_path, mode="rb"),
            encoding="utf8",
            errors="replace",
        )
        # Fixing bytes read as string because of Python2 pickling
        cls.po_class_object.img_as_png = cls.po_class_object.img_as_png.encode("utf8")

        cls.maxDiff = None

    def test_save_po_object_class(self) -> None:
        """Check save page object class."""
        if is_windows():
            self.skipTest(
                "Unsupported in Windows because temp directory is hardcoded to '/tmp' in pickled object.",
            )
        else:
            for path in (self.po_class_object.file_path, self.po_class_object.img_path):
                safe_remove_path(path)

            self.po_class_object.save()

            check_if_path_exists(self.po_class_object.file_path)
            assert Path(self.po_class_object.file_path).stat().st_size
            check_if_path_exists(self.po_class_object.img_path)
            assert Path(self.po_class_object.img_path).stat().st_size

    def test_get_formatted_fields(self) -> None:
        """Check get formatted fields."""
        if is_windows():
            self.skipTest(
                "Unsupported in Windows because temp directory is hardcoded to '/tmp' in pickled object.",
            )
        else:
            expected_fields = """
    BAD_NAME = (By.LINK_TEXT, u'⇶') # location: (1261, 23) dimensions: (33, 33)
    LOGO_HOMEPAGE_LINK = (By.ID, u'logo_homepage_link') # location: (526, 117) dimensions: (250, 200)
    SEARCH_FORM_INPUT_HOMEPAGE = (By.ID, u'search_form_input_homepage') # location: (347, 347) dimensions: (562, 46)
    SEARCH_BUTTON_HOMEPAGE = (By.ID, u'search_button_homepage') # location: (912, 350) dimensions: (52, 40)
    TAG_HOME_NAV_TAG_HOME_NAV_ITEM = (By.CSS_SELECTOR, u'.tag-home__nav > .tag-home__nav__item') # location: (625, 458) dimensions: (7, 7)
    TAG_HOME_NAV_ITEM_IS_ACTIVE = (By.CSS_SELECTOR, u'.tag-home__nav__item.is-active') # location: (658, 458) dimensions: (7, 7)
    ADD_TO_BROWSER_BADGE_ICON_BROWSER_FIREFOX = (By.CSS_SELECTOR, u'.add-to-browser-badge__icon.browser--firefox') # location: (518, 521) dimensions: (64, 64)
    ID_FOOTER_HOMEPAGE_DIV_1_SPAN_1_BR_1 = (By.XPATH, u'id("footer_homepage")/DIV[1]/SPAN[1]/BR[1]') # location: (747, 572) dimensions: (0, 20)
    DDGSI_ADD_TO_BROWSER_BADGE_CLOSE_JS_ADD_TO_BROWSER_CLOSE = (By.CSS_SELECTOR, u'.ddgsi.add-to-browser-badge__close.js-add-to-browser-close') # location: (754, 559) dimensions: (30, 38)
"""
            assert (
                self.po_class_object._get_fields_as_code().strip()
                == expected_fields.strip()
            )

    def test_get_file_content(self) -> None:
        """Check get file content."""
        if is_windows():
            self.skipTest(
                "Unsupported in Windows because temp directory is hardcoded to '/tmp' in pickled object.",
            )
        else:
            expected_string = read_file(self.expected_duckduckgo_class_path)
            assert (
                self.po_class_object._get_file_content().strip()
                == expected_string.strip()
            )

    def test_get_by_as_code_str(self) -> None:
        """Check get by as code str."""
        assert get_by_as_code_str(By.ID) == "By.ID"
        assert get_by_as_code_str(By.CLASS_NAME) == "By.CLASS_NAME"
        assert get_by_as_code_str(By.XPATH) == "By.XPATH"
        assert get_by_as_code_str(By.CSS_SELECTOR) == "By.CSS_SELECTOR"
        assert get_by_as_code_str(By.LINK_TEXT) == "By.LINK_TEXT"

    def test_get_by_from_code_str(self) -> None:
        """Check get by from code str."""
        assert get_by_from_code_str("By.ID") == By.ID
        assert get_by_from_code_str("By.CLASS_NAME") == By.CLASS_NAME
        assert get_by_from_code_str("By.XPATH") == By.XPATH
        assert get_by_from_code_str("By.CSS_SELECTOR") == By.CSS_SELECTOR
        assert get_by_from_code_str("By.LINK_TEXT") == By.LINK_TEXT

    def test_parse_string_to_po_class(self) -> None:
        """Check parse string to page object class."""
        if is_windows():
            self.skipTest(
                "Unsupported in Windows because temp directory is hardcoded to '/tmp' in pickled object.",
            )
        else:
            expected_string = read_file(self.expected_duckduckgo_class_path)
            assert (
                self.po_class_object._get_file_content().strip()
                == expected_string.strip()
            )

            po_class = PageObjectClass.parse_string_to_po_class(
                read_file(self.expected_duckduckgo_class_path),
            )

            assert po_class.name == self.po_class_object.name
            assert po_class.url == self.po_class_object.url
            assert po_class.fields == self.po_class_object.fields
            assert po_class.area == self.po_class_object.area
            assert po_class.file_path == self.po_class_object.file_path
            assert po_class.img_path == self.po_class_object.img_path

            assert po_class == self.po_class_object
