# coding=utf8
import os
import traceback
from tempfile import gettempdir

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from easelenium.mouse import Mouse
from easelenium.utils import get_random_value, get_timestamp, is_windows


def browser_decorator(
    browser_name=None, timeout=5, logger=None, headless=False, webdriver_kwargs=None
):
    def func_decorator(func):
        def wrapper(*args, **kwargs):
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
            except Exception:
                try:
                    if browser:
                        browser.save_screenshot()
                except Exception:
                    pass
                traceback.print_exc()
            finally:
                if browser:
                    browser.quit()

            return return_value

        return wrapper

    return func_decorator


class Browser(object):
    FF = "ff"
    FF_HEADLESS = "ff_headless"
    GC = "gc"
    GC_HEADLESS = "gc_headless"
    IE = "ie"
    OP = "op"
    PHANTOMJS = "phantomjs"
    DEFAULT_BROWSER = None

    __BROWSERS = [FF, FF_HEADLESS, GC, GC_HEADLESS, IE, OP, PHANTOMJS]

    __DRIVERS_AND_CONSTUCTORS = driver_and_constructor = {
        FF: ("geckodriver", "Firefox"),
        FF_HEADLESS: ("geckodriver", "Firefox"),
        IE: ("IEDriverServer", "Ie"),
        GC: ("chromedriver", "Chrome"),
        GC_HEADLESS: ("chromedriver", "Chrome"),
        OP: ("operadriver", "Opera"),
        PHANTOMJS: ("phantomjs", "PhantomJS"),
    }
    __LOCATOR_MAPPINGS = {
        "by_name": By.NAME,
        "by_id": By.ID,
        "by_xpath": By.XPATH,
        "by_link": By.LINK_TEXT,
        "by_partial_link": By.PARTIAL_LINK_TEXT,
        "by_tag": By.TAG_NAME,
        "by_class": By.CLASS_NAME,
        "by_css": By.CSS_SELECTOR,
    }

    def __init__(
        self,
        browser_name=None,
        logger=None,
        timeout=5,
        headless=False,
        webdriver_kwargs=None,
    ):
        if webdriver_kwargs is None:
            webdriver_kwargs = {}

        self.__browser_name = self.DEFAULT_BROWSER or browser_name or self.FF

        self.logger = logger
        self.__timeout = timeout

        headless = headless or "headless" in self.__browser_name
        if self.is_gc():
            self.__set_chrome_kwargs(headless, webdriver_kwargs)
        elif self.is_ff():
            self.__set_firefox_kwargs(headless, webdriver_kwargs)

        self._driver = self.__create_driver(self.__browser_name, webdriver_kwargs)
        self.__screenshot_path = os.path.join(gettempdir(), "easelenium_screenshots")

        if not os.path.exists(self.__screenshot_path):
            os.makedirs(self.__screenshot_path)

        self.mouse = Mouse(self)

    def __set_chrome_kwargs(self, headless, webdriver_kwargs):
        options = webdriver_kwargs.get("options", webdriver.ChromeOptions())
        if headless:
            options.add_argument("--headless")
        webdriver_kwargs["options"] = options

    def __set_firefox_kwargs(self, headless, webdriver_kwargs):
        options = webdriver_kwargs.get("options", webdriver.FirefoxOptions())
        if headless:
            options.add_argument("--headless")
        webdriver_kwargs["options"] = options

    @classmethod
    def supports(cls, browser_name):
        return cls._find_driver_path(browser_name) is not None

    @classmethod
    def _find_driver_path(cls, browser_name):
        assert browser_name in cls.__BROWSERS

        driver_filename = cls.__DRIVERS_AND_CONSTUCTORS[browser_name][0]
        if is_windows():
            driver_filename += ".exe"

        possible_path = os.path.join(os.path.expanduser("~"), driver_filename)
        if os.path.exists(possible_path):
            return possible_path
        else:
            for folder in os.getenv("PATH", "").split(os.pathsep):
                possible_path = os.path.join(folder, driver_filename)
                if os.path.exists(possible_path):
                    return possible_path

        return None

    @classmethod
    def get_supported_browsers(cls):
        return cls.__BROWSERS

    def get_browser_initials(self):
        return self.__browser_name

    def __create_driver(self, name, webdriver_kwargs):
        driver_filename_and_constructor = self.__DRIVERS_AND_CONSTUCTORS.get(name, None)

        if driver_filename_and_constructor is None:
            browsers = "', '".join(self.__BROWSERS)
            raise ValueError(
                f"Unsupported browser '{name}', supported browsers: ['{browsers}']"
            )

        driver_filename, constructor = driver_filename_and_constructor
        constructor = getattr(webdriver, constructor)

        driver_path = webdriver_kwargs.get("executable_path") or self._find_driver_path(
            name
        )
        if driver_path is None:
            raise FileNotFoundError(f"Failed to find {driver_filename}")

        webdriver_kwargs["executable_path"] = driver_path

        driver = constructor(**webdriver_kwargs)

        if driver and not self.is_gc() and not self.is_op():
            driver.maximize_window()

        return driver

    def get_by_query(
        self,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        # TODO: move outside
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
        else:
            raise ValueError("Failed to find element")

    def _get_element(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        assert (
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
        else:
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

    def __get_webelements(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
        elif type(element) in [list, tuple] and len(element) == 2:
            if parent:
                return parent.find_elements(*element)
            else:
                return self._driver.find_elements(*element)
        else:
            raise Exception("Unsupported element - %s" % str(element))

    def __get_by_and_locator(self, element):
        # TODO: remove not needed
        if (type(element) == list or type(element) == tuple) and len(element) == 2:
            by, locator = element
            return by, locator
        else:
            return None

    def _to_string(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        # TODO: move outside
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
        by_and_locator = self.__get_by_and_locator(element)
        if by_and_locator:
            return "Element {By: '%s', value: '%s'}" % (
                by_and_locator[0],
                by_and_locator[1],
            )
        else:
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

    def is_ff(self):
        return self.__browser_name.startswith(Browser.FF)

    def is_ie(self):
        return self.__browser_name == Browser.IE

    def is_gc(self):
        return self.__browser_name.startswith(Browser.GC)

    def is_op(self):
        return self.__browser_name == Browser.OP

    def _safe_log(self, *args):
        if self.logger:
            args = [
                self._to_string(arg) if isinstance(arg, WebElement) else arg
                for arg in args
            ]
            self.logger.info(*args)

    """
        WebElement's wrapped functions
    """

    def type(
        self,
        element=None,
        text=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
            if "Element must be user-editable in order to clear it." != e.msg:
                raise e

        self._safe_log("Typing '%s' at '%s'", text, element)

        element.send_keys(text)

    def click(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_parent(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_text(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
        text = element.text

        self._safe_log("Getting text from '%s' -> '%s'", element, text)

        return text

    def get_attribute(
        self,
        element=None,
        attr=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
        visible=True,
    ):
        assert attr is not None, "attr is not specified"
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

    def get_tag_name(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_id(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
        visible=False,
    ):
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

    def get_class(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
        visible=False,
    ):
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

    def get_value(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
        visible=True,
    ):
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

    def get_location(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_dimensions(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_selected_value_from_dropdown(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_selected_text_from_dropdown(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def select_option_by_value_from_dropdown(
        self,
        element=None,
        value=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
        assert value is not None, "value not specified"

        self._safe_log(f"Selecting by value {value} from {element}")

        select.select_by_value(value)

    def select_option_by_text_from_dropdown(
        self,
        element=None,
        text=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def select_option_by_index_from_dropdown(
        self,
        element=None,
        index=0,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def select_random_option_from_dropdown(
        self,
        element=None,
        texts_to_skip=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def get_texts_from_dropdown(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

        texts = []
        element = self.find_element(element=element, parent=parent)
        for option in Select(element).options:
            texts.append(option.text)

        self._safe_log("Getting texts from '%s' -> '%s'", element, str(texts))

        return texts

    def get_values_from_dropdown(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

        values = []
        element = self.find_element(element=element, parent=parent)
        for option in Select(element).options:
            values.append(option.get_attribute("value"))

        self._safe_log("Getting values from '%s' -> '%s'", element, str(values))

        return values

    """
        WebDriver's wrapped functions
    """

    def get_action_chains(self):
        return ActionChains(self._driver)

    def open(self, url):
        self.get(url)

    def get(self, url):
        self._driver.get(url)

    def execute_js(self, js_script, *args):
        return self._driver.execute_script(js_script, *args)

    def find_element(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def find_descendant(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
        if len(found_elements) == 0:
            raise NoSuchElementException(
                "Didn't find any elements for selector - %s" % str(element)
            )
        else:
            return found_elements[0]

    def find_elements(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
        parent=None,
    ):
        elements = self.__get_webelements(
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
        if type(elements) == list:
            return elements
        else:
            return [elements]

    def find_descendants(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def wait_for_text_is_changed(
        self,
        element=None,
        old_text=None,
        parent=None,
        msg=None,
        timeout=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s text was not changed for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: old_text
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

    def wait_for_attribute_is_changed(
        self,
        element=None,
        attr=None,
        old_value=None,
        parent=None,
        msg=None,
        timeout=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s attribute was not changed for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: old_value
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

    def wait_for_visible(
        self,
        element=None,
        msg=None,
        timeout=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
            msg = "%s is not visible for %s seconds" % (element, timeout)
        self.webdriver_wait(
            lambda driver: self.is_visible(element=element, parent=parent),
            msg,
            timeout,
        )

    def wait_for_not_visible(
        self,
        element=None,
        msg=None,
        timeout=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
            msg = "%s is visible for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: not self.is_visible(element=element, parent=parent),
            msg,
            timeout,
        )

    def wait_for_present(
        self,
        element=None,
        msg=None,
        timeout=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is not present for %s seconds" % (element, timeout)

        self.webdriver_wait(lambda driver: self.is_present(element), msg, timeout)

    def wait_for_not_present(
        self,
        element=None,
        msg=None,
        timeout=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is present for %s seconds" % (element, timeout)

        self.webdriver_wait(lambda driver: not self.is_present(element), msg, timeout)

    def is_visible(
        self,
        element=None,
        parent=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def is_present(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
                )
            )
            > 0
        )

    def get_screenshot_as_png(self):
        return self._driver.get_screenshot_as_png()

    def save_screenshot(self, saving_dir=None, filename=None):
        if not saving_dir:
            saving_dir = self.__screenshot_path
        if not filename:
            filename = get_timestamp() + ".png"
        path_to_file = os.path.abspath(os.path.join(saving_dir, filename))

        self._safe_log("Saving screenshot to '%s'", path_to_file)

        self._driver.save_screenshot(path_to_file)
        return path_to_file

    def get_elements_count(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
            )
        )

    def switch_to_frame(
        self,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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

    def switch_to_new_window(
        self,
        function,
        element=None,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
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
            lambda driver: len(initial_handles) < len(driver.window_handles)
        )
        new_handles = self._driver.window_handles
        for handle in initial_handles:
            new_handles.remove(handle)

        self._driver.switch_to.window(new_handles[0])

        self._safe_log("Switching to '%s' window", self._driver.title)

    def switch_to_default_content(self):
        self._safe_log("Switching to default content")

        self._driver.switch_to.default_content()

    def close_current_window_and_focus_to_previous_one(self):
        handles = self._driver.window_handles
        self.close()
        self._driver.switch_to.window(handles[-2])

    def get_page_source(self):
        return self._driver.page_source

    def get_title(self):
        return self._driver.title

    def get_current_url(self):
        return self._driver.current_url

    def get_current_frame_url(self):
        return self.execute_js("return document.location.href")

    def go_back(self):
        self._driver.back()

    def delete_all_cookies(self):
        self._driver.delete_all_cookies()

    def alert_accept(self):
        self._safe_log("Clicking Accept/OK in alert box")

        self._driver.switch_to.alert.accept()

    def alert_dismiss(self):
        self._safe_log("Clicking Dismiss/Cancel in alert box")

        self._driver.switch_to.alert.dismiss()

    def refresh_page(self):
        self._driver.refresh()

    def webdriver_wait(self, function, msg="", timeout=None):
        if not timeout:
            timeout = self.__timeout
        try:
            WebDriverWait(self._driver, timeout).until(function, msg)
        except Exception:
            raise TimeoutException(msg)

    def close(self):
        self._driver.close()

    def quit(self):
        self._driver.quit()
