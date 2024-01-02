"""Browser module."""
from __future__ import annotations

import os
import tempfile
import traceback
from functools import lru_cache
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, Final, Tuple, Union

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import Chrome, Edge, Firefox, Ie
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.ie.service import Service as IeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager, IEDriverManager

from easelenium.mouse import Mouse
from easelenium.utils import Logger, get_random_value, get_timestamp

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

TypeElement = Union[WebElement, Tuple[str, str]]


def browser_decorator(
    browser_name: str | None = None,
    timeout: float = 5,
    logger: Logger = None,
    *,
    headless: bool = False,
    webdriver_kwargs: dict[str, Any] | None = None,
) -> Any:  # noqa: ANN401
    """Python decorator with Browser initialization."""

    def func_decorator(func: callable) -> Any:  # noqa: ANN401
        def wrapper(*args: list[Any], **kwargs: dict[str, Any]) -> Any:  # noqa: ANN401
            browser = None
            return_value = None
            try:
                browser = Browser(
                    browser_name=browser_name,
                    logger=logger,
                    timeout=timeout,
                    headless=headless,
                    webdriver_kwargs=webdriver_kwargs,
                )

                kwargs["browser"] = browser
                value = func(*args, **kwargs)
                return_value = value
            except Exception:  # noqa: BLE001
                try:
                    if browser:
                        browser.save_screenshot()
                except Exception:  # noqa: BLE001, S110
                    pass
                traceback.print_exc()
            finally:
                if browser:
                    browser.quit()

            return return_value

        return wrapper

    return func_decorator


class Browser:
    """Browser class."""

    FF: Final = "ff"
    FF_HEADLESS: Final = "ff_headless"
    GC: Final = "gc"
    GC_HEADLESS: Final = "gc_headless"
    IE: Final = "ie"
    EDGE: Final = "edge"
    DEFAULT_BROWSER = None

    __BROWSERS: Final = [
        FF,
        FF_HEADLESS,
        GC,
        GC_HEADLESS,
        IE,
        EDGE,
    ]

    __DRIVERS_MAPPING: Final = {
        FF: ("geckodriver", Firefox, FirefoxService),
        FF_HEADLESS: ("geckodriver", Firefox, FirefoxService),
        IE: ("IEDriverServer", Ie, IeService),
        EDGE: ("EdgeDriverServer", Edge, EdgeService),
        GC: ("chromedriver", Chrome, ChromeService),
        GC_HEADLESS: ("chromedriver", Chrome, ChromeService),
    }
    __LOCATOR_MAPPINGS: Final = {
        "by_name": By.NAME,
        "by_id": By.ID,
        "by_xpath": By.XPATH,
        "by_link": By.LINK_TEXT,
        "by_partial_link": By.PARTIAL_LINK_TEXT,
        "by_tag": By.TAG_NAME,
        "by_class": By.CLASS_NAME,
        "by_css": By.CSS_SELECTOR,
    }

    def __init__(  # noqa: PLR0913
        self,
        browser_name: str | None = None,
        logger: Logger | None = None,
        timeout: float = 5,
        *,
        headless: bool = False,
        maximize: bool = True,
        webdriver_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize."""
        if webdriver_kwargs is None:
            webdriver_kwargs = {}

        self.__browser_name = self.DEFAULT_BROWSER or browser_name or self.FF

        self.logger = logger
        self.__timeout = timeout

        headless = headless or "headless" in self.__browser_name
        if self.is_gc():
            self.__set_chrome_kwargs(
                headless=headless,
                webdriver_kwargs=webdriver_kwargs,
            )
        elif self.is_ff():
            self.__set_firefox_kwargs(
                headless=headless,
                webdriver_kwargs=webdriver_kwargs,
            )

        self._driver = self.__create_driver(self.__browser_name, webdriver_kwargs)
        if maximize:
            self._driver.maximize_window()

        screenshot_path = Path(gettempdir()) / "easelenium_screenshots"
        self.__screenshot_path = str(screenshot_path)

        if not screenshot_path.exists():
            screenshot_path.mkdir(parents=True, exist_ok=True)

        self.mouse = Mouse(self)

    def __set_chrome_kwargs(
        self,
        *,
        headless: bool,
        webdriver_kwargs: dict[str, Any],
    ) -> None:
        options = webdriver_kwargs.get("options", ChromeOptions())
        is_root = os.getuid() == 0
        if is_root:
            options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless")
        webdriver_kwargs["options"] = options

    def __set_firefox_kwargs(
        self,
        *,
        headless: bool,
        webdriver_kwargs: dict[str, Any],
    ) -> None:
        options = webdriver_kwargs.get("options", FirefoxOptions())
        if headless:
            options.add_argument("--headless")
        webdriver_kwargs["options"] = options

    @classmethod
    def supports(cls: type[Browser], browser_name: str) -> bool:
        """Return True if browser is supported, False otherwise."""
        return cls._find_driver_path(browser_name) is not None

    @classmethod
    @lru_cache(maxsize=None)
    def _find_driver_path(cls: type[Browser], browser_name: str) -> str | None:
        """Return driver path."""
        assert browser_name in cls.__BROWSERS  # noqa: S101
        assert browser_name in cls.__DRIVERS_MAPPING  # noqa: S101

        service_klass = cls.__DRIVERS_MAPPING[browser_name][2]

        if service_klass == FirefoxService:
            geckodriver_snap = Path("/snap/bin/geckodriver")
            if geckodriver_snap.exists():
                driver_path = geckodriver_snap.as_posix()
            else:
                driver_path = GeckoDriverManager().install()
            return driver_path
        if service_klass == ChromeService:
            manager = ChromeDriverManager
        elif service_klass == IeService:
            manager = IEDriverManager
        elif service_klass == EdgeService:
            manager = EdgeChromiumDriverManager

        try:
            return manager().install()
        except AttributeError:
            return None

    @classmethod
    def get_supported_browsers(cls: type[Browser]) -> list[str]:
        """Return supported browsers."""
        return cls.__BROWSERS

    def get_browser_initials(self) -> str | None:
        """Return browser initials."""
        return self.__browser_name

    def __create_driver(self, name: str, webdriver_kwargs: dict[str, Any]) -> WebDriver:
        if os.environ.get("TMPDIR") is None:
            # fix TMPDIR if not exists
            os.environ["TMPDIR"] = tempfile.gettempdir()

        driver_filename_and_constructor = self.__DRIVERS_MAPPING.get(name, None)

        if driver_filename_and_constructor is None:
            browsers = "', '".join(self.__BROWSERS)
            msg = f"Unsupported browser '{name}', supported browsers: ['{browsers}']"
            raise ValueError(msg)

        driver_filename, constructor, service_klass = driver_filename_and_constructor

        driver_path = webdriver_kwargs.get("executable_path") or self._find_driver_path(
            name,
        )
        if not driver_path:
            msg = f"Failed to find driver manager for {name}"
            raise ValueError(msg)

        webdriver_kwargs["service"] = service_klass(driver_path)
        if "executable_path" in webdriver_kwargs:
            webdriver_kwargs.pop("executable_path")

        return constructor(**webdriver_kwargs)

    def get_by_query(  # noqa: PLR0913
        self,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> TypeElement:
        """Return element as tuple[str, str] by query."""
        # TODO: move outside  # noqa: TD003, FIX002, TD002
        for locator, value in (
            ("by_id", by_id),
            ("by_xpath", by_xpath),
            ("by_tag", by_tag),
            ("by_name", by_name),
            ("by_css", by_css),
            ("by_class", by_class),
            ("by_link", by_link),
            ("by_partial_link", by_partial_link),
        ):
            if value is not None:
                return (self.__LOCATOR_MAPPINGS[locator], value)

        msg = "Failed to find element"
        raise ValueError(msg)

    def _get_element(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> TypeElement | WebElement:
        assert (  # noqa: S101
            element is not None
            or by_id is not None
            or by_xpath is not None
            or by_link is not None
            or by_partial_link is not None
            or by_name is not None
            or by_tag is not None
            or by_css is not None
            or by_class is not None
        ), "'element' or 'by_*' not specified"

        if element:
            return element

        return self.get_by_query(
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def __get_webelements(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> list[WebElement]:
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if isinstance(element, WebElement):
            return [element]

        if parent:
            assert isinstance(element, (list, tuple))  # noqa: S101
            if isinstance(parent, WebElement):
                return parent.find_elements(*element)

            parent = self._driver.find_element(*parent)
            return parent.find_elements(*element)

        return self._driver.find_elements(*element)

    def to_string(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> str:
        """Return element as string."""
        # TODO: move outside  # noqa: TD002, TD003, FIX002
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if isinstance(element, WebElement):
            string = "tag_name: '%s'" % element.tag_name
            _id = element.get_attribute("id")
            if _id:
                string += ", id: '%s'" % _id
            class_name = element.get_attribute("class")
            if class_name:
                string += ", class: '%s'" % class_name
            text = element.text
            if text:
                string += ", text: '%s'" % text
            value = element.get_attribute("value")
            if value:
                string += ", value: '%s'" % value
            name = element.get_attribute("name")
            if name and element.tag_name in ["frame", "iframe"]:
                string += ", name: '%s'" % name
            return "Element {%s}" % string

        return f"Element {{By: '{element[0]}', value: '{element[1]}'}}"

    def is_ff(self) -> bool:
        """Return True if browser is Firefox."""
        return self.__browser_name.startswith(Browser.FF)

    def is_ie(self) -> bool:
        """Return True if browser is Internet Explorer."""
        return self.__browser_name == Browser.IE

    def is_gc(self) -> bool:
        """Return True if browser is Google Chrome."""
        return self.__browser_name.startswith(Browser.GC)

    def _safe_log(self, *args: list[Any]) -> None:
        if self.logger:
            args = [
                self.to_string(arg) if isinstance(arg, WebElement) else str(arg)
                for arg in args
            ]
            self.logger.info(*args)

    """
        WebElement's wrapped functions
    """

    def type(  # noqa: PLR0913, A003
        self,
        element: TypeElement | WebElement | None = None,
        text: str | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Type text at element."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

        self.wait_for_visible(element=element, parent=parent)
        element = self.find_element(element=element, parent=parent)
        try:
            element.clear()
        except WebDriverException as e:
            if e.msg != "Element must be user-editable in order to clear it.":
                raise

        self._safe_log("Typing '%s' at '%s'", text, element)

        element.send_keys(text)

    def click(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Click on element."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)
        element = self.find_element(element=element, parent=parent)

        self._safe_log("Clicking at '%s'", element)

        element.click()

    def get_parent(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> WebElement:
        """Return parent element."""
        element = self.find_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        return self.find_descendant(parent=element, by_xpath="./..")

    def get_text(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        *,
        visible: bool = True,
    ) -> str:
        """Return text of the element."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if visible:
            self.wait_for_visible(element=element, parent=parent)
        element = self.find_element(element=element, parent=parent)
        text = element.text

        self._safe_log("Getting text from '%s' -> '%s'", element, text)

        return text

    def get_attribute(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        attr: str | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        *,
        visible: bool = False,
    ) -> str:
        """Return attribute of the element."""
        assert attr is not None, "attr is not specified"  # noqa: S101
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if visible:
            self.wait_for_visible(element=element, parent=parent)
        element = self.find_element(element=element, parent=parent)
        value = element.get_attribute(attr)

        self._safe_log(f"Getting attribute {attr} from {element} -> {value}")

        return value

    def get_tag_name(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> str:
        """Return tag name of the element."""
        return self.find_element(
            element=element,
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        ).tag_name

    def get_id(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        *,
        visible: bool = False,
    ) -> str:
        """Return id of the element."""
        return self.get_attribute(
            element=element,
            attr="id",
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
            visible=visible,
        )

    def get_class(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        *,
        visible: bool = False,
    ) -> str:
        """Return class of the element."""
        return self.get_attribute(
            element=element,
            attr="class",
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
            visible=visible,
        )

    def get_value(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        *,
        visible: bool = True,
    ) -> str:
        """Return value of the element."""
        return self.get_attribute(
            element=element,
            attr="value",
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
            visible=visible,
        )

    def get_location(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> tuple[int, int]:
        """Return tuple like (x, y)."""
        location = self.find_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        ).location

        self._safe_log(f"Getting location from {element} -> {location}")

        return int(location["x"]), int(location["y"])

    def get_dimensions(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> tuple[int | float, int | float]:
        """Return tuple like (width, height)."""
        size = self.find_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        ).size

        self._safe_log(f"Getting dimensions from {element} -> {size}")

        return size["width"], size["height"]

    """
        Dropdown list related methods
    """

    def get_selected_value_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> str:
        """Return value of the selected option."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        value = Select(element).first_selected_option.get_attribute("value")

        self._safe_log("Getting selected value from '%s' -> '%s'", element, value)

        return value

    def get_selected_text_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> str:
        """Return text of the selected option."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)

        text = Select(element).first_selected_option.text

        self._safe_log("Getting selected text from '%s' -> '%s'", element, text)

        return text

    def select_option_by_value_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        value: str | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Select option by value."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        select = Select(element)
        assert value is not None, "value not specified"  # noqa: S101

        self._safe_log(f"Selecting by value {value} from {element}")

        select.select_by_value(value)

    def select_option_by_text_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        text: str | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Select option by text."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        select = Select(element)

        self._safe_log(f"Selecting by text {text} from {element}")

        select.select_by_visible_text(text)

    def select_option_by_index_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        index: int = 0,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Select option by index."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        select = Select(element)

        self._safe_log(f"Selecting by index {index} from {element}")

        select.select_by_index(index)

    def select_random_option_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        texts_to_skip: set[str] | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Select random option from dropdown."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)
        texts_to_skip = texts_to_skip or []

        options = self.get_texts_from_dropdown(
            element=element,
        )
        option_to_select = get_random_value(options, *texts_to_skip)

        self.select_option_by_text_from_dropdown(
            element=element,
            text=option_to_select,
        )

    def get_texts_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> list[str]:
        """Return list of texts from dropdown."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        texts = [option.text for option in Select(element).options]

        self._safe_log("Getting texts from '%s' -> '%s'", element, str(texts))

        return texts

    def get_values_from_dropdown(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> list[str]:
        """Return list of values from dropdown."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        self.wait_for_visible(element=element, parent=parent)

        element = self.find_element(element=element, parent=parent)
        values = [option.get_attribute("value") for option in Select(element).options]

        self._safe_log("Getting values from '%s' -> '%s'", element, str(values))

        return values

    """
        WebDriver's wrapped functions
    """

    def get_action_chains(self) -> ActionChains:
        """Return ActionChains instance."""
        return ActionChains(self._driver)

    def open(self, url: str) -> None:  # noqa: A003
        """Open url."""
        self.get(url)

    def get(self, url: str) -> None:
        """Open url."""
        self._driver.get(url)

    def execute_js(self, js_script: str, *args: list[str]) -> str:
        """Execute javascript."""
        return self._driver.execute_script(js_script, *args)

    def find_element(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> WebElement:
        """Find element."""
        return self.find_descendant(
            element=element,
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def find_descendant(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> WebElement:
        """Find descendant."""
        found_elements = self.find_descendants(
            element=element,
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if found_elements:
            return found_elements[0]

        raise NoSuchElementException(
            "Didn't find any elements for selector - %s" % str(element),
        )

    def find_elements(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
        parent: TypeElement | WebElement | None = None,
    ) -> list[WebElement]:
        """Find element."""
        return self.__get_webelements(
            element=element,
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def find_descendants(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> list[WebElement]:
        """Find descendant."""
        return self.__get_webelements(
            element=element,
            parent=parent,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def wait_for_text_is_changed(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        old_text: str | None = None,
        parent: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait for text is changed."""
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = f"{element} text was not changed for {timeout} seconds"

        self.webdriver_wait(
            lambda _driver: old_text
            != self.get_text(
                element,
                parent=parent,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            ),
            msg,
            timeout,
        )

    def wait_for_attribute_is_changed(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        attr: str | None = None,
        old_value: str | None = None,
        parent: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait for attribute is changed."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = (
                f"{self.to_string(element)} attribute "
                f"was not changed for {timeout} seconds"
            )

        self.webdriver_wait(
            lambda _driver: old_value
            != self.get_attribute(
                element=element,
                attr=attr,
                parent=parent,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
                visible=False,
            ),
            msg,
            timeout,
        )

    def wait_for_visible(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait until element is visible."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = f"{element} is not visible for {timeout} seconds"
        self.webdriver_wait(
            lambda _driver: self.is_visible(element=element, parent=parent),
            msg,
            timeout,
        )

    def wait_for_not_visible(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait until element not is visible."""
        element = self._get_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = f"{element} is visible for {timeout} seconds"

        self.webdriver_wait(
            lambda _driver: not self.is_visible(element=element, parent=parent),
            msg,
            timeout,
        )

    def wait_for_present(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        parent: TypeElement | WebElement | None = None,  # noqa: ARG002
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait until element is present."""
        if not timeout:
            timeout = self.__timeout
            msg = f"{element} is not present for {timeout} seconds"

        self.webdriver_wait(
            lambda _driver: self.is_present(
                element,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            ),
            msg,
            timeout,
        )

    def wait_for_not_present(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        msg: str | None = None,
        timeout: float | None = None,
        parent: TypeElement | WebElement | None = None,  # noqa: ARG002
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Wait until element is not present."""
        if not timeout:
            timeout = self.__timeout
            msg = f"{element} is present for {timeout} seconds"

        self.webdriver_wait(
            lambda _driver: not self.is_present(
                element,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            ),
            msg,
            timeout,
        )

    def is_visible(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        parent: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> bool:
        """Return True if element is visible."""
        if parent:
            elements = self.find_descendants(
                element=element,
                parent=parent,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            )
        else:
            elements = self.find_elements(
                element=element,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            )
        return len(elements) > 0 and elements[0].is_displayed()

    def is_present(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> bool:
        """Return True if element is present."""
        return (
            len(
                self.find_elements(
                    element=element,
                    by_id=by_id,
                    by_xpath=by_xpath,
                    by_link=by_link,
                    by_partial_link=by_partial_link,
                    by_name=by_name,
                    by_tag=by_tag,
                    by_css=by_css,
                    by_class=by_class,
                ),
            )
            > 0
        )

    def get_screenshot_as_png(self) -> Any:  # noqa: ANN401
        """Return screenshot in bytes."""
        return self._driver.get_screenshot_as_png()

    def save_screenshot(
        self,
        saving_dir: str | None = None,
        filename: str | None = None,
    ) -> str:
        """Save screenshot to file."""
        if not saving_dir:
            saving_dir = self.__screenshot_path
        if not filename:
            filename = get_timestamp() + ".png"
        path_to_file = str((Path(saving_dir) / filename).absolute())

        self._safe_log("Saving screenshot to '%s'", path_to_file)

        self._driver.save_screenshot(path_to_file)
        return path_to_file

    def get_elements_count(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> int:
        """Return number of elements."""
        return len(
            self.find_elements(
                element=element,
                by_id=by_id,
                by_xpath=by_xpath,
                by_link=by_link,
                by_partial_link=by_partial_link,
                by_name=by_name,
                by_tag=by_tag,
                by_css=by_css,
                by_class=by_class,
            ),
        )

    def switch_to_frame(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Switch context to new frame."""
        element = self.find_element(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

        self._safe_log("Switching to '%s' frame", element)

        self._driver.switch_to.frame(element)

    def switch_to_new_window(  # noqa: PLR0913
        self,
        function: callable,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Switch context to new window."""
        initial_handles = self._driver.window_handles

        function(
            element=element,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

        self.webdriver_wait(
            lambda driver: len(initial_handles) < len(driver.window_handles),
        )
        new_handles = self._driver.window_handles
        for handle in initial_handles:
            new_handles.remove(handle)

        self._driver.switch_to.window(new_handles[0])

        self._safe_log("Switching to '%s' window", self._driver.title)

    def switch_to_default_content(self) -> None:
        """Switch to default content."""
        self._safe_log("Switching to default content")

        self._driver.switch_to.default_content()

    def close_current_window_and_focus_to_previous_one(self) -> None:
        """Close current window and switch to previous one."""
        handles = self._driver.window_handles
        self.close()
        self._driver.switch_to.window(handles[-2])

    def get_page_source(self) -> str:
        """Return page source."""
        return self._driver.page_source

    def get_title(self) -> str:
        """Return page title."""
        return self._driver.title

    def get_current_url(self) -> str:
        """Return current url."""
        return self._driver.current_url

    def get_current_frame_url(self) -> str:
        """Return current frame url."""
        return self.execute_js("return document.location.href")

    def go_back(self) -> None:
        """Go back."""
        self._driver.back()

    def delete_all_cookies(self) -> None:
        """Delete all cookies."""
        self._driver.delete_all_cookies()

    def alert_accept(self) -> None:
        """Accept modal window."""
        self._safe_log("Clicking Accept/OK in alert box")

        self._driver.switch_to.alert.accept()

    def alert_dismiss(self) -> None:
        """Dismiss model window."""
        self._safe_log("Clicking Dismiss/Cancel in alert box")

        self._driver.switch_to.alert.dismiss()

    def refresh_page(self) -> None:
        """Refresh page."""
        self._driver.refresh()

    def webdriver_wait(
        self,
        function: callable,
        msg: str = "",
        timeout: float | None = None,
    ) -> None:
        """Wait for condition."""
        if not timeout:
            timeout = self.__timeout
        try:
            WebDriverWait(self._driver, timeout).until(function, msg)
        except Exception as exc:  # noqa: BLE001
            raise TimeoutException(msg) from exc

    def close(self) -> None:
        """Close browser."""
        self._driver.close()

    def quit(self) -> None:  # noqa: A003
        """Close browser."""
        self._driver.quit()
