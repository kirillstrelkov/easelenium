"""Page object class."""
from __future__ import annotations

import ast
from pathlib import Path

from selenium.webdriver.common.by import By

from easelenium.ui.file_utils import safe_create_path, save_file
from easelenium.utils import LINESEP, get_match


def get_by_as_code_str(by: str) -> str:
    """Get the By enum literal as a Python code string."""
    value = None
    if by == By.LINK_TEXT:
        value = "By.LINK_TEXT"
    elif by == By.CLASS_NAME:
        value = "By.CLASS_NAME"
    elif by == By.CSS_SELECTOR:
        value = "By.CSS_SELECTOR"
    elif by == By.XPATH:
        value = "By.XPATH"
    elif by == By.ID:
        value = "By.ID"

    if value:
        return value

    raise NotImplementedError


def get_by_from_code_str(by_as_string: str) -> str:
    """Get the By enum value from the By literal as a string."""
    value = None
    if by_as_string == "By.LINK_TEXT":
        value = By.LINK_TEXT
    elif by_as_string == "By.CLASS_NAME":
        value = By.CLASS_NAME
    elif by_as_string == "By.CSS_SELECTOR":
        value = By.CSS_SELECTOR
    elif by_as_string == "By.XPATH":
        value = By.XPATH
    elif by_as_string == "By.ID":
        value = By.ID

    if value:
        return value

    raise NotImplementedError


class PageObjectClassField:
    """Page object class field."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        by: str,
        selector: str,
        location: tuple[int, int],
        dimensions: tuple[int, int],
    ) -> None:
        """Initialize."""
        self.name = name
        self.by = by
        self.selector = selector
        self.location = location
        self.dimensions = dimensions

    def __eq__(self, other: PageObjectClass) -> bool:
        """Return True if two PageObjectClassField are equal else False."""
        return (other is not None) and (
            self.name == other.name
            and self.by == other.by
            and self.selector == other.selector
        )

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return str(self)

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return f"PageObjectClassField({self.__dict__})"


class PageObjectClass:
    """Page object class."""

    IMAGE_FOLDER = "img"
    TEMPLATE = """# coding=utf8
from selenium.webdriver.common.by import By

from easelenium.base_page_object import BasePageObject


class {name}(BasePageObject):
    # Please do NOT remove auto-generated comments
    # Url: {url}
    # Area: {area}
    # File path: {file_path}
    # Image path: {img_path}
{fields_as_code}

"""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        url: str,
        fields: list[str],
        area: tuple[int, int] | None = None,
        file_path: str | None = None,
        img_path: str | None = None,
        img_as_png: str | None = None,
    ) -> None:
        """Initialize."""
        self.name = name
        self.url = url
        self.fields = fields
        self.area = area
        self.file_path = file_path
        self.img_as_png = img_as_png
        self.img_path = img_path

    def save(self, new_folder: str | None = None) -> None:
        """Save the class to a file."""
        if new_folder:
            py_filename = Path(self.file_path).name
            img_filename = Path(self.img_path).name
            self.file_path = str(Path(new_folder) / py_filename)
            self.img_path = str(
                (Path(new_folder) / self.IMAGE_FOLDER / img_filename),
            )
        safe_create_path(self.file_path)
        safe_create_path(self.img_path)
        save_file(self.file_path, self._get_file_content())
        save_file(self.img_path, self.img_as_png, is_text=False)

    def _get_file_content(self) -> str:
        """Get formatted file content."""
        kwargs = self.__dict__.copy()
        fields_as_code = self._get_fields_as_code()
        if len(fields_as_code.strip()) == 0:
            fields_as_code = "    pass" + LINESEP
        kwargs["fields_as_code"] = fields_as_code
        return self.TEMPLATE.format(**kwargs)

    def _get_fields_as_code(self) -> str:
        single_line = "    {name} = ({by_as_code}, u'{selector}') # {comment}"
        lines = [
            single_line.format(
                name=field.name,
                by_as_code=get_by_as_code_str(field.by),
                selector=field.selector.replace("'", "\\'"),
                comment=f"location: {field.location} dimensions: {field.dimensions}",
            )
            for field in self.fields
        ]

        return LINESEP.join(lines)

    @classmethod
    def parse_string_to_po_class(
        cls: type[PageObjectClass],
        string: str,
    ) -> PageObjectClass:
        """Parse a string to a PageObjectClass object."""
        name_regexp = r"class (\w+)\(BasePageObject\):"
        url_regexp = r"Url: (.+)"
        area_regexp = r"Area: \(?([\w, ]+)\)?"
        img_path_regexp = r"Image path: (.+)"
        file_path_regexp = r"File path: (.+)"
        fields_regexp = r"\s+(\w+) = (.+) # location: (.+) dimensions: (.+)"

        name = get_match(name_regexp, string)
        url = get_match(url_regexp, string)
        area = ast.literal_eval(get_match(area_regexp, string))
        img_path = get_match(img_path_regexp, string)
        file_path = get_match(file_path_regexp, string)
        tmp_fields = get_match(fields_regexp, string, single_match=False)
        fields = []

        if tmp_fields:
            for (
                field_name,
                field_by_and_selector,
                field_location,
                field_dimensions,
            ) in tmp_fields:
                by, selector = eval(field_by_and_selector)  # noqa: S307, PGH001
                location = ast.literal_eval(field_location)
                dimensions = ast.literal_eval(field_dimensions)
                po_class_field = PageObjectClassField(
                    field_name,
                    by,
                    selector,
                    location,
                    dimensions,
                )
                fields.append(po_class_field)

        return PageObjectClass(name, url, fields, area, file_path, img_path)

    def __eq__(self, other: PageObjectClass) -> bool:
        """Return True if two PageObjectClass are equal else False."""
        return (
            self.name == other.name
            and self.url == other.url
            and self.fields == other.fields
            and self.area == other.area
            and self.file_path == other.file_path
            and self.img_path == other.img_path
        )

    def __repr__(self) -> None:
        """Return a string representation of the object."""
        return str(self)

    def __str__(self) -> None:
        """Return a string representation of the object."""
        return f"PageObjectClass({self.__dict__})"
