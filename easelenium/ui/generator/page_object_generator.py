"""PageObjectGenerator class."""
from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from wx import Point, Rect

from easelenium.ui.file_utils import check_if_path_exists, read_file
from easelenium.ui.generator.page_object_class import (
    PageObjectClass,
    PageObjectClassField,
)
from easelenium.ui.root_folder import RootFolder
from easelenium.utils import get_py_file_name_from_class_name

if TYPE_CHECKING:
    from loguru import Logger

    from easelenium.browser import Browser, TypeElement
    from easelenium.ui.utils import TypeArea, TypeBy, TypePoint

# TODO: when generating link_text - escape new lines  # noqa: TD003, TD002, FIX002


class PageObjectGenerator:
    """PageObjectGenerator class."""

    GET_XPATH_USING_JS = read_file(
        str(Path(__file__).parent / "get_xpath.js"),
    )
    ELEMENTS_SELECTOR = (
        By.CSS_SELECTOR,
        "[onclick], [jsaction], a, select, button, input, "
        "span, p, h1, h2, h3, h4, h5, h6, "
        "frame, iframe, .btn",
    )
    FRAMES_SELECTOR = (By.CSS_SELECTOR, "frame, iframe")

    def __init__(self, browser: Browser, logger: Logger = None) -> None:
        """Initialize."""
        self.browser = browser
        self.logger = logger

    def __log(self, *msgs: list[str]) -> None:
        if self.logger:
            self.logger.info(" ".join([str(m) for m in msgs]))

    def _get_name_for_field(
        self,
        element_or_by_and_selector: TypeElement,
    ) -> str:
        max_length = 30
        if isinstance(element_or_by_and_selector, WebElement):
            by_and_selector = self._get_selector(element_or_by_and_selector)
        else:
            by_and_selector = element_or_by_and_selector
        name = "_".join(
            [w.upper()[:max_length] for w in re.findall(r"\w+", by_and_selector[1])],
        )
        name = re.sub(r"_+", "_", name)
        if len(name) == 0:
            name = "BAD_NAME"
        return name

    def __is_correct_element(
        self,
        element: TypeElement,
        area: TypeArea,
        location_offset: TypePoint,
    ) -> bool:
        bad_element_tags = ("option", "script")

        if area:
            if type(area) not in (tuple, list) or len(area) != 4:  # noqa: PLR2004
                msg = f"Bad area data '{area}'"
                raise ValueError(msg)
            area = Rect(*area)
            x, y = self.browser.get_location(element)
            if location_offset:
                # fixing location because it is located inside frame
                x += location_offset[0]
                y += location_offset[1]
            w, h = self.browser.get_dimensions(element)
            element_center = Point(int(x + w / 2), int(y + h / 2))
            is_element_inside = area.Contains(element_center)
        else:
            is_element_inside = True

        return (
            self.browser.is_visible(element)
            and element.tag_name not in bad_element_tags
            and is_element_inside
        )

    def __get_po_fields_from_page(
        self,
        area: TypeArea,
        location_offset: TypePoint | None = None,
    ) -> list[PageObjectClassField]:
        fields = []
        elements = self.browser.find_elements(self.ELEMENTS_SELECTOR)
        i = 1
        log_prefix = " " * 10
        for e in elements:
            if self.logger:
                self.__log(
                    "%5d/%d Trying to get PageObjectField for element %s"
                    % (i, len(elements), self.browser.to_string(e)),
                )

            if self.__is_correct_element(e, area, location_offset):
                field = self.__get_pageobject_field(e, location_offset)
                if field:
                    self.__log(log_prefix, "PageObjectField:", field)
                    fields.append(field)
                else:
                    self.__log(log_prefix, "Failed to unique selector")
            else:
                self.__log(
                    log_prefix,
                    "Skipped - element is not supported/visible or is outside of area",
                )
            i += 1

        self.__log("Number of fields:", len(fields))
        return fields

    def get_all_po_fields(
        self,
        url: str,
        area: TypeArea | None = None,
    ) -> list[PageObjectClassField]:
        """Get all PO fields for page."""
        if self.browser.get_current_url() != url:
            self.browser.get(url)

        fields = []
        self.browser.switch_to_default_content()
        self.__log("Getting fields for main content")
        fields += self.__get_po_fields_from_page(area)

        for frame in self.browser.find_elements(self.FRAMES_SELECTOR):
            self.browser.switch_to_default_content()
            location_offset = self.browser.get_location(frame)

            if self.logger:
                self.__log(
                    "Getting fields for frame",
                    self.browser.to_string(frame),
                )

            self.browser.switch_to_frame(frame)

            fields += self.__get_po_fields_from_page(area, location_offset)

        self.__log("Total number of fields:", len(fields))

        names = []
        for field in fields:
            if field.name in names:
                uniq_name = False
                i = 0
                while not uniq_name:
                    new_name = "_".join([field.name, str(i)])
                    if new_name not in names:
                        uniq_name = True
                        field.name = new_name
                    i += 1
            names.append(field.name)

        return fields

    def get_po_class_for_url(
        self,
        url: str,
        class_name: str,
        folder_path: str,
        area: TypeArea | None = None,
    ) -> PageObjectClass:
        """Get PageObjectClass for url."""
        po_folder = str(Path(folder_path) / RootFolder.PO_FOLDER)
        img_folder = str(
            Path(folder_path) / RootFolder.PO_FOLDER / PageObjectClass.IMAGE_FOLDER,
        )
        check_if_path_exists(folder_path)

        self.__log(
            f"Generating PageObjectClass for url {url} with area {area}",
        )
        fields = self.get_all_po_fields(url, area)
        img_as_png = self.browser.get_screenshot_as_png()

        filename = get_py_file_name_from_class_name(class_name)
        file_path = str(Path(po_folder) / filename)
        img_path = str(
            Path(img_folder) / Path(filename).parent / (Path(filename).stem + ".png"),
        )

        return PageObjectClass(
            class_name,
            url,
            fields,
            area,
            file_path,
            img_path,
            img_as_png,
        )

    def __get_pageobject_field(
        self,
        element: TypeElement,
        location_offset: TypePoint,
    ) -> PageObjectClassField | None:
        by_and_selector = self._get_selector(element)
        if by_and_selector:
            by, selector = by_and_selector

            name = self._get_name_for_field(by_and_selector)
            is_frame = self.browser.find_element(element).tag_name in [
                "frame",
                "iframe",
            ]
            if is_frame:
                name = "FRAME_" + name
            name_starts_with_number = re.match(r"^\d+.+$", name)
            if name_starts_with_number:
                name = "N" + name

            location = self.browser.get_location(element)
            if location_offset:
                # fix location because it is inside frame
                location = (
                    location[0] + location_offset[0],
                    location[1] + location_offset[1],
                )
            dimensions = self.browser.get_dimensions(element)
            return PageObjectClassField(name, by, selector, location, dimensions)
        return None

    def _get_selector(self, element: TypeElement) -> TypeBy | None:
        for selector_func in (
            self._get_id_selector,
            self._get_link_text_selector,
            self._get_class_name_selector,
            self._get_css_selector,
            self._get_xpath_selector,
        ):
            by_and_selector = selector_func(element)
            if by_and_selector:
                return by_and_selector

        return None

    def _get_id_selector(self, element: TypeElement) -> TypeBy | None:
        _id = self.browser.get_id(element)
        if _id and len(self.browser.find_elements(by_id=_id)) == 1:
            return By.ID, _id

        return None

    def _get_css_selector(self, element: TypeElement) -> TypeBy | None:
        """
        Recursively tries to find unique CSS selector for given element.

        Goes up through DOM tree until HTML or BODY tag is found. If
        doesn't find unique selector returns None.

        """
        element = self.browser.find_element(element)
        cur_css_selector = ""
        _id = element.get_attribute("id").strip()

        if _id:
            cur_css_selector += "#%s" % _id
        else:
            class_name = element.get_attribute("class").strip()

            if class_name:
                class_name = re.sub(r"\s+", ".", class_name)
                cur_css_selector += ".%s" % class_name

        cur_css_selector = cur_css_selector.replace(":", r"\:")
        cur_el_tag = element.tag_name
        if cur_el_tag in ("body", "html") or len(cur_css_selector) == 0:
            return None

        by_and_css_selector = By.CSS_SELECTOR, cur_css_selector
        elements_count = self.browser.get_elements_count(by_and_css_selector)
        if elements_count == 1:
            return by_and_css_selector

        parent = self.browser.get_parent(element)
        css_parent_selector = self._get_css_selector(parent)
        if css_parent_selector:
            new_css_selector = " > ".join(
                (css_parent_selector[1], cur_css_selector),
            )
            return By.CSS_SELECTOR, new_css_selector

        return None

    def _get_xpath_selector(self, element: TypeElement) -> TypeBy:
        return By.XPATH, self.browser.execute_js(self.GET_XPATH_USING_JS, element)

    def _get_link_text_selector(self, element: TypeBy) -> TypeBy | None:
        text = self.browser.get_text(element)
        if len(self.browser.find_elements((By.LINK_TEXT, text))) == 1 and len(text) > 1:
            return By.LINK_TEXT, text

        return None

    def _get_class_name_selector(self, element: TypeBy) -> TypeBy | None:
        class_name = self.browser.get_class(element)
        if (
            len(class_name) > 0
            and " " not in class_name
            and len(self.browser.find_elements((By.CLASS_NAME, class_name))) == 1
        ):
            return By.CLASS_NAME, class_name

        return None
