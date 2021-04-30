# coding=utf8
import os
import tempfile
import traceback
from functools import wraps
from tempfile import gettempdir, tempdir

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from easelenium.utils import get_random_value, get_timestamp, is_windows


def stale_exception_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return_value = None
        try:
            return_value = func(*args, **kwargs)
        except StaleElementReferenceException:
            return_value = func(*args, **kwargs)
        finally:
            return return_value

    return wrapper


class Mouse(object):
    def __init__(self, browser):
        self.browser = browser

    def left_click(self, element):
        self.left_click_by_offset(element, 0, 0)

    def left_click_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)

        if type(element) == tuple:
            element = self.browser.find_element(element)

        self.browser._safe_log(
            "Click at '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(
            xoffset, yoffset
        ).click().perform()

    def hover(self, element):
        self.browser._safe_log("Hover at '%s'", element)

        self.hover_by_offset(element, 0, 0)

    def hover_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)

        element = self.browser.find_element(element)

        self.browser._safe_log(
            "Mouse over '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(xoffset, yoffset).perform()

    def right_click(self, element):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)

        if type(element) == tuple:
            element = self.browser.find_element(element)

        self.browser._safe_log("Right click at '%s'", self.browser._to_string(element))

        actions.context_click(element).perform()

    def right_click_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)

        if type(element) == tuple:
            element = self.browser.find_element(element)

        self.browser._safe_log(
            "Right click at '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(
            xoffset, yoffset
        ).context_click().perform()


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
        FF: ("geckodriver", webdriver.Firefox),
        FF_HEADLESS: ("geckodriver", webdriver.Firefox),
        IE: ("IEDriverServer", webdriver.Ie),
        GC: ("chromedriver", webdriver.Chrome),
        GC_HEADLESS: ("chromedriver", webdriver.Chrome),
        OP: ("operadriver", webdriver.Opera),
        PHANTOMJS: ("phantomjs", webdriver.PhantomJS),
    }

    def __init__(self, browser_name=None, webdriver_kwargs=None, **browser_kwargs):
        if webdriver_kwargs is None:
            webdriver_kwargs = {}

        browser_name = browser_kwargs.get("name", browser_name)
        self.__browser_name = self.DEFAULT_BROWSER or browser_name or self.FF

        self.logger = browser_kwargs.get("logger", None)
        self.__timeout = browser_kwargs.get("timeout", 5)

        headless = browser_kwargs.get("headless", "headless" in self.__browser_name)
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
    def _find_driver_path(cls, browser_name, **webdriver_kwargs):
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

        driver_path = self._find_driver_path(name, **webdriver_kwargs)
        if driver_path is None:
            raise FileNotFoundError(f"Failed to find {driver_filename}")

        webdriver_kwargs["executable_path"] = driver_path

        driver = constructor(**webdriver_kwargs)

        if driver and not self.is_gc() and not self.is_op():
            driver.maximize_window()

        return driver

    def __get_webelements(self, element, parent=None):
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
        if (type(element) == list or type(element) == tuple) and len(element) == 2:
            by, locator = element
            return by, locator
        else:
            return None

    def _to_string(self, element):
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
        return self.__browser_name == Browser.FF

    def is_ie(self):
        return self.__browser_name == Browser.IE

    def is_gc(self):
        return self.__browser_name == Browser.GC

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

    def type(self, element, text):
        self.wait_for_visible(element)
        element = self.find_element(element)
        try:
            element.clear()
        except WebDriverException as e:
            if "Element must be user-editable in order to clear it." != e.msg:
                raise e

        self._safe_log("Typing '%s' at '%s'", text, element)

        element.send_keys(text)

    def click(self, element):
        self.wait_for_visible(element)
        element = self.find_element(element)

        self._safe_log("Clicking at '%s'", element)

        element.click()

    def get_parent(self, element):
        element = self.find_element(element)
        parent = element.parent
        if isinstance(parent, WebElement):
            return parent
        else:
            return self.find_descendant(element, (By.XPATH, "./.."))

    def get_text(self, element):
        self.wait_for_visible(element)
        element = self.find_element(element)
        text = element.text

        self._safe_log("Getting text from '%s' -> '%s'", element, text)

        return text

    def get_attribute(self, element, attr):
        self.wait_for_visible(element)
        element = self.find_elements(element)[0]
        value = element.get_attribute(attr)

        self._safe_log("Getting attribute '%s' from '%s' -> '%s'", attr, element, value)

        return value

    def get_tag_name(self, element):
        return self.find_element(element).tag_name

    def get_id(self, element):
        return self.get_attribute(element, "id")

    def get_class(self, element):
        return self.get_attribute(element, "class")

    def get_value(self, element):
        return self.get_attribute(element, "value")

    def get_location(self, element):
        """Return tuple like (x, y)."""
        location = self.find_element(element).location

        self._safe_log("Getting location from '%s' -> '%s'", element, str(location))

        return int(location["x"]), int(location["y"])

    def get_dimensions(self, element):
        """Return tuple like (width, height)."""
        size = self.find_element(element).size

        self._safe_log("Getting dimensions from '%s' -> '%s'", element, str(size))

        return size["width"], size["height"]

    """
        Dropdown list related methods
    """

    def get_selected_value_from_dropdown(self, element):
        self.wait_for_visible(element)

        element = self.find_element(element)
        value = Select(element).first_selected_option.get_attribute("value")

        self._safe_log("Getting selected value from '%s' -> '%s'", element, value)

        return value

    def get_selected_text_from_dropdown(self, element):
        self.wait_for_visible(element)

        element = self.find_element(element)

        text = Select(element).first_selected_option.text

        self._safe_log("Getting selected text from '%s' -> '%s'", element, text)

        return text

    def select_option_by_value_from_dropdown(self, element, value):
        self.wait_for_visible(element)

        element = self.find_element(element)
        select = Select(element)

        self._safe_log("Selecting by value '%s' from '%s'", value, element)

        select.select_by_value(value)

    def select_option_by_text_from_dropdown(self, element, text):
        self.wait_for_visible(element)

        element = self.find_element(element)
        select = Select(element)

        self._safe_log("Selecting by text '%s' from '%s'", text, element)

        select.select_by_visible_text(text)

    def select_option_by_index_from_dropdown(self, element, index):
        self.wait_for_visible(element)

        element = self.find_element(element)
        select = Select(element)

        self._safe_log("Selecting by index '%s' from '%s'", index, element)

        select.select_by_index(index)

    def select_random_option_from_dropdown(self, element, *texts_to_skip):
        self.wait_for_visible(element)

        options = self.get_texts_from_dropdown(element)
        option_to_select = get_random_value(options, *texts_to_skip)

        self.select_option_by_text_from_dropdown(element, option_to_select)

    def get_texts_from_dropdown(self, element):
        self.wait_for_visible(element)

        texts = []
        element = self.find_element(element)
        for option in Select(element).options:
            texts.append(option.text)

        self._safe_log("Getting texts from '%s' -> '%s'", element, str(texts))

        return texts

    def get_values_from_dropdown(self, element):
        self.wait_for_visible(element)

        values = []
        element = self.find_element(element)
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

    def find_element(self, element):
        return self.find_descendant(None, element)

    def find_descendant(self, parent, element):
        found_elements = self.find_descendants(parent, element)
        if len(found_elements) == 0:
            raise NoSuchElementException(
                "Didn't find any elements for selector - %s" % str(element)
            )
        else:
            return found_elements[0]

    def find_elements(self, element):
        elements = self.__get_webelements(element)
        if type(elements) == list:
            return elements
        else:
            return [elements]

    def find_descendants(self, parent, element):
        return self.__get_webelements(element, parent)

    def wait_for_text_is_changed(self, element, old_text, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s text was not changed for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: old_text != self.get_text(element), msg, timeout
        )

    def wait_for_attribute_is_changed(
        self, element, attr, old_value, msg=None, timeout=None
    ):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s attribute was not changed for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: old_value != self.get_attribute(element, attr, False),
            msg,
            timeout,
        )

    def wait_for_visible(self, element, msg=None, timeout=None, parent=None):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s is not visible for %s seconds" % (element, timeout)

        self.webdriver_wait(
            lambda driver: self.is_visible(element, parent), msg, timeout
        )

    def wait_for_not_visible(self, element, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s is visible for %s seconds" % (element, timeout)

        self.webdriver_wait(lambda driver: not self.is_visible(element), msg, timeout)

    def wait_for_present(self, element, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is not present for %s seconds" % (element, timeout)

        self.webdriver_wait(lambda driver: self.is_present(element), msg, timeout)

    def wait_for_not_present(self, element, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is present for %s seconds" % (element, timeout)

        self.webdriver_wait(lambda driver: not self.is_present(element), msg, timeout)

    def is_visible(self, element, parent=None):
        try:
            if parent:
                elements = self.find_descendants(parent, element)
            else:
                elements = self.find_elements(element)
            return len(elements) > 0 and elements[0].is_displayed()
        except WebDriverException:
            return False

    def is_present(self, element):
        return len(self.find_elements(element)) > 0

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

    def get_elements_count(self, element):
        return len(self.find_elements(element))

    def switch_to_frame(self, element):
        element = self.find_element(element)

        self._safe_log("Switching to '%s' frame", element)

        self._driver.switch_to.frame(element)

    def switch_to_new_window(self, function, *args):
        initial_handles = self._driver.window_handles

        function(*args)

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
        except:
            raise TimeoutException(msg)

    def close(self):
        self._driver.close()

    def quit(self):
        self._driver.quit()
