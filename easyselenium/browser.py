# coding=utf8
import os
import tempfile

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException

from easyselenium.utils import get_random_value, get_timestamp


class Mouse(object):
    def __init__(self, browser, logger=None):
        self.browser = browser
        self.logger = logger
    
    def left_click(self, element):
        self.left_click_by_offset(element, 0, 0)
    
    def left_click_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)
        
        if type(element) == tuple:
            element = self.browser.find_element(element)
        
        if self.logger:
            self.logger.info(u"Click at '%s' by offset(%s,%s)",
                             self.browser._to_string(element), 
                             xoffset, 
                             yoffset)
        
        actions.move_to_element(element)\
            .move_by_offset(xoffset, yoffset).click().perform()
        
    def hover(self, element):
        self.hover_by_offset(element, 0, 0)
        
    def hover_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)
        
        element = self.browser.find_element(element)
        
        if self.logger:
            self.logger.info(u"Mouse over '%s' by offset(%s,%s)",
                             self.browser._to_string(element), 
                             xoffset, 
                             yoffset)
        
        actions.move_to_element(element)\
            .move_by_offset(xoffset, yoffset).perform()
        
    def right_click(self, element):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)
        
        if type(element) == tuple:
            element = self.browser.find_element(element)
        
        if self.logger:
            self.logger.info(u"Right click at '%s'",
                             self.browser._to_string(element))
        
        actions.context_click(element).perform()
        
    def right_click_by_offset(self, element, xoffset, yoffset):
        actions = self.browser.get_action_chains()
        self.browser.wait_for_visible(element)
        
        if type(element) == tuple:
            element = self.browser.find_element(element)
        
        if self.logger:
            self.logger.info(u"Right click at '%s' by offset(%s,%s)",
                             self.browser._to_string(element), 
                             xoffset, 
                             yoffset)
        
        actions.move_to_element(element)\
            .move_by_offset(xoffset, yoffset).context_click().perform()


class Browser(object):
    FF = 'ff'
    GC = 'gc'
    IE = 'ie'
    OP = 'op'

    __BROWSERS = [FF, GC, IE, OP]

    def __init__(self, browser_name=FF, logger=None, timeout=5):
        self.logger = logger
        self.__timeout = timeout
        self.__browser_name = browser_name
        self._driver = self.__create_driver(browser_name)
        self.mouse = Mouse(self, self.logger)

    def __create_driver(self, name):
        if name == self.IE:
            return webdriver.Ie()
        elif name == self.GC:
            path_to_chromedriver = os.path.join(os.path.expanduser("~"),
                                                "chromedriver")
            if os.path.exists(path_to_chromedriver):
                return webdriver.Chrome(executable_path=path_to_chromedriver)
            else:
                raise Exception("Chromedriver wasn't found in " + 
                                path_to_chromedriver)
        elif name == self.OP:
            path_to_selenium_server = os.path.join(
                os.path.expanduser("~"),
                "selenium-server-standalone.jar"
            )
            if os.path.exists(path_to_selenium_server):
                return webdriver.Opera(executable_path=path_to_selenium_server)
            else:
                raise Exception("Selenium server jar file wasn't found in " + 
                                path_to_selenium_server)
        elif name == self.FF:
            return webdriver.Firefox()
        else:
            raise ValueError(
                "Unsupported browser '%s', " \
                "supported browsers: ['%s']" % (name,
                                                "', '".join(self.__BROWSERS))
            )
    
    def __get_webelement(self, element, single_element=True):
        if isinstance(element, WebElement):
            return element
        elif type(element) in [list, tuple] and len(element) == 2:
            if single_element:
                return self._driver.find_element(*element)
            else:
                return self._driver.find_elements(*element)
        else:
            raise Exception("Unsupported element " + str(element))
    
    def __get_by_and_locator(self, element):
        if (type(element) == list or type(element) == tuple) and \
            len(element) == 2:
            by, locator = element
            return by, locator
        else:
            return None
    
    def _to_string(self, element):
        by_and_locator = self.__get_by_and_locator(element)
        if by_and_locator:
            return "Element {By: '%s', value: '%s'}" % (by_and_locator[0], 
                                                        by_and_locator[1])
        else:
            string = ""
            text = element.text
            value = element.get_attribute('value')
            if text:
                string += "text: '%s'" % text
            if value:
                string += "value: '%s'" % value
            return "Element {%s}" % string
    
    def is_ff(self):
        return self.__browser_name == Browser.FF
    
    def is_ie(self):
        return self.__browser_name == Browser.IE
    
    def is_gc(self):
        return self.__browser_name == Browser.GC
    
    def is_op(self):
        return self.__browser_name == Browser.OP
    
    """
        WebElement's wrapped functions
    """
    def get_text(self, element):
        self.wait_for_visible(element)
        element = self.find_element(element)
        return element.text

    def type(self, element, text):
        self.wait_for_visible(element)
        element = self.find_element(element)
        try:
            element.clear()
        except WebDriverException as e:
            if u'Element must be user-editable in order to clear it.' != e.msg:
                raise e

        if self.logger:
            self.logger.info(u"Typing '%s' at '%s'",
                             text, 
                             self._to_string(element))

        element.send_keys(text)

    def click(self, element):
        self.wait_for_visible(element)
        element = self.find_element(element)
        
        if self.logger:
            self.logger.info(u"Clicking at '%s'", self._to_string(element))
        
        element.click()

    def get_attribute(self, element, attr):
        self.wait_for_visible(element)
        element = self.find_element(element)
        return element.get_attribute(attr)

    def get_value(self, element):
        return self.get_attribute(element, "value")

    """
        Dropdown list related methods
    """
    def get_selected_value_of_dropdown(self, element):
        self.wait_for_visible(element)
        
        element = self.find_element(element)
        return Select(element).first_selected_option.get_attribute('value') # TODO
    
    def get_selected_text_of_dropdown(self, element):
        self.wait_for_visible(element)
        
        element = self.find_element(element)
        return Select(element).first_selected_option.text

    def select_option_by_value_from_dropdown(self, element, value):
        self.wait_for_visible(element)
        
        element = self.find_element(element)
        select = Select(element)
        
        if self.logger:
            self.logger.info(u"Selecting by value '%s' from dropdown list", 
                             value)
        
        select.select_by_value(value)

    def select_option_by_text_from_dropdown(self, element, text):
        self.wait_for_visible(element)
        
        element = self.find_element(element)
        select = Select(element)
        
        if self.logger:
            self.logger.info(u"Selecting by text '%s' from dropdown list", text)
        
        select.select_by_visible_text(text)

    def select_option_by_index_from_dropdown(self, element, index):
        self.wait_for_visible(element)
        
        element = self.find_element(element)
        select = Select(element)
        if self.logger:
            self.logger.info(u"Selecting by index'%s' from dropdown list", index)
        
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
        
        return texts

    def get_values_from_dropdown(self, element):
        self.wait_for_visible(element)
        
        values = []
        element = self.find_element(element)
        for option in Select(element).options:
            values.append(option.get_attribute('value')) # TODO)
        
        return values

    """
        WebDriver's wrapped functions
    """
    def get_action_chains(self):
        return ActionChains(self._driver)

    def get(self, url):
        self._driver.get(url)

    def execute_js(self, js_script):
        return self._driver.execute_script(js_script)

    def find_element(self, element):
        return self.__get_webelement(element)

    def find_elements(self, element):
        elements = self.__get_webelement(element, False)
        if type(elements) == list:
            return elements
        else:
            return [elements]

    def wait_for_visible(self, element, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s is not visible for %s seconds" % \
                  (self._to_string(element), timeout)

        self.webdriver_wait(lambda driver: self.is_visible(element),
                            msg,
                            timeout)

    def wait_for_not_visible(self, element, msg=None, timeout=None):
        if not timeout:
            timeout = self.__timeout
        if not msg:
            msg = "%s is visible for %s seconds" % \
                  (self._to_string(element), timeout)
      
        self.webdriver_wait(lambda driver: not self.is_visible(element),
                            msg,
                            timeout)

    def wait_for_present(self, element, timeout=None):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is not present for %s seconds" % \
                  (self._to_string(element), timeout)

        self.webdriver_wait(lambda driver: self.is_present(element),
                            msg,
                            timeout)

    def wait_for_not_present(self, element, timeout=None):
        if not timeout:
            timeout = self.__timeout
            msg = "%s is present for %s seconds" % \
                  (self._to_string(element), timeout)
        
        self.webdriver_wait(lambda driver: not self.is_present(element),
                            msg,
                            timeout)

    def is_visible(self, element):
        try:
            elements = self.find_elements(element)
            return elements and len(elements) > 0 and \
                   elements[0].is_displayed()
        except WebDriverException as e:
            print e
            return False

    def is_present(self, element):
        return len(self.find_elements(element)) > 0

    def save_screenshot(self, saving_dir=None):
        if not saving_dir:
            saving_dir = tempfile.gettempdir()
        path_to_file = os.path.abspath(os.path.join(saving_dir,
                                                    get_timestamp() + ".png"))
        
        if self.logger:
            self.logger.info(u"Saving screenshot to '%s'", path_to_file)
        
        self._driver.save_screenshot(path_to_file)

    def get_elements_count(self, element):
        return len(self.find_elements(element))

    def switch_to_frame(self, element):
        element = self.find_element(element)
        
        if self.logger:
            self.logger.info(u"Switching to '%s' frame", 
                             self._to_string(element))

        self._driver.switch_to_frame(element)

    def switch_to_new_window(self, function, *args):
        initial_handles = self._driver.window_handles

        function(*args)

        self.webdriver_wait(
            lambda driver: len(initial_handles) < len(driver.window_handles)
        )
        new_handles = self._driver.window_handles
        for handle in initial_handles:
            new_handles.remove(handle)

        self._driver.switch_to_window(new_handles[0])

        if self.logger:
            self.logger.info(u"Switching to '%s' window", self._driver.title)

    def switch_to_default_content(self):
        if self.logger:
            self.logger.info(u"Switching to default content")
        
        self._driver.switch_to_default_content()

    def close_current_window_and_focus_to_previous_one(self):
        handles = self._driver.window_handles
        self.close()
        self._driver.switch_to_window(handles[-2])

    def get_page_source(self):
        return self._driver.page_source
    
    def get_title(self):
        return self._driver.title
    
    def get_current_url(self):
        return self._driver.current_url
    
    def go_back(self):
        self._driver.back()

    def delete_all_cookies(self):
        self._driver.delete_all_cookies()

    def alert_accept(self):
        if self.logger:
            self.logger.info(u"Clicking Accept/OK in alert box")
        self._driver.switch_to_alert().accept()

    def alert_dismiss(self):
        if self.logger:
            self.logger.info(u"Clicking Dismiss/Cancel in alert box")
        self._driver.switch_to_alert().dismiss()

    def refresh_page(self):
        self._driver.refresh()

    def webdriver_wait(self, function, msg='', timeout=None):
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
