# coding=utf8
import os
import re

from selenium.webdriver.common.by import By
from easyselenium.utils import unicode_str
from easyselenium.file_utils import check_if_path_exists
from easyselenium.generator.page_object_class import PageObjectClassField, \
    PageObjectClass
from selenium.webdriver.remote.webelement import WebElement
from wx import Point, Rect
from time import sleep
from easyselenium.ui.root_folder import RootFolder
from easyselenium.ui.utils import get_py_file_name_from_class_name


class PageObjectGenerator(object):
    # js code ref. -
    # http://stackoverflow.com/questions/2631820/im-storing-click-coordinates-in-my-db-and-then-reloading-them-later-and-showing/2631931
    GET_XPATH_USING_JS = '''function getPathTo(element) {
    if (element.id!=='')
        return 'id("'+element.id+'")';
    if (element===document.body)
        return element.tagName;

    var ix= 0;
    var siblings= element.parentNode.childNodes;
    for (var i= 0; i<siblings.length; i++) {
        var sibling= siblings[i];
        if (sibling===element)
            return getPathTo(element.parentNode)+'/'+element.tagName+'['+(ix+1)+']';
        if (sibling.nodeType===1 && sibling.tagName===element.tagName)
            ix++;
    }
}
return getPathTo(arguments[0]);'''

    def __init__(self, browser):
        self.browser = browser

    def __log(self, *msgs):
        # TODO: implement correct logging
        print u" ".join([unicode_str(msg) for msg in msgs])

    def _filter_elements(self, elements, area=None):
        bad_element_tags = ['option', 'script']

        def is_correct_element(element, area):
            if area:
                if type(area) not in (tuple, list) or len(area) != 4:
                    raise Exception(u"Bad area data '%s'" % str(area))
                area = Rect(*area)
                x, y = self.browser.get_location(element)
                w, h = self.browser.get_dimensions(element)
                element_center = Point(x + w / 2, y + h / 2)
                is_element_inside = area.Contains(element_center)
            else:
                is_element_inside = True
            return (is_element_inside and
                    self.browser.is_visible(element) and
                    not element.tag_name in bad_element_tags)

        elements = [e for e in elements if is_correct_element(e, area)]
        return elements

    def _get_elements_from_url(self, url):
        if self.browser.get_current_url() != url:
            self.browser.get(url)
            sleep(3)  # sleep for 3 sec

        # NOTE: CSS 3 selectors are used
        elements = self.browser.find_elements(
            (By.CSS_SELECTOR,
             ':only-child, a, select, button, input, span')
        )

        return elements

    def _get_name_for_field(self, element_or_by_and_selector):
        max_length = 30
        if isinstance(element_or_by_and_selector, WebElement):
            by_and_selector = self._get_selector(element_or_by_and_selector)
        else:
            by_and_selector = element_or_by_and_selector
        name = u'_'.join([w.upper()[:max_length]
                          for w in re.findall(r'\w+', by_and_selector[1])])
        name = re.sub(r'_+', u'_', name)
        if len(name) == 0:
            name = u'BAD_NAME'
        return name

    def get_po_class_for_url(self, url, class_name, folder_path, area=None):
        po_folder = os.path.join(folder_path,
                                 RootFolder.PO_FOLDER)
        img_folder = os.path.join(folder_path,
                                  RootFolder.PO_FOLDER,
                                  PageObjectClass.IMAGE_FOLDER)
        check_if_path_exists(folder_path)

        elements = self._get_elements_from_url(url)
        elements = self._filter_elements(elements, area)

        fields = self._get_po_class_fields_from_elements(elements)
        img_as_png = self.browser.get_screenshot_as_png()

        filename = get_py_file_name_from_class_name(class_name)
        file_path = os.path.join(po_folder, filename)
        img_path = os.path.join(img_folder,
                                os.path.splitext(filename)[0] + '.png')

        return PageObjectClass(class_name, url, fields,
                               area, file_path, img_path,
                               img_as_png)

    def _get_po_class_fields_from_elements(self, elements):
        class_fields = []
        for element in elements:
            by_and_selector = self._get_selector(element)
            if by_and_selector:
                by, selector = by_and_selector
                name = self._get_name_for_field(by_and_selector)
                location = self.browser.get_location(element)
                dimensions = self.browser.get_dimensions(element)
                po_class_field = PageObjectClassField(name,
                                                      by,
                                                      selector,
                                                      location,
                                                      dimensions)
                if po_class_field not in class_fields:
                    class_fields.append(po_class_field)
        return class_fields

    def _get_selector(self, element):
        for selector_func in (self._get_id_selector,
                              self._get_link_text_selector,
                              self._get_class_name_selector,
                              self._get_css_selector,
                              self._get_xpath_selector):
            if self.browser.is_visible(element):
                by_and_selector = selector_func(element)
                if by_and_selector:
                    return by_and_selector

        return None

    def _get_id_selector(self, element):
        _id = self.browser.get_id(element)
        if len(self.browser.find_elements((By.ID, _id))) == 1:
            return By.ID, _id
        else:
            return None

    def _get_class_name_selector(self, element):
        class_name = self.browser.get_class(element)
        if (len(class_name) > 0 and
                u' ' not in class_name and
                len(self.browser.find_elements((By.CLASS_NAME, class_name))) == 1):
            return By.CLASS_NAME, class_name
        else:
            return None

    def _get_css_selector(self, element):
        """Recursively tries to find unique CSS selector for given element.

        Goes up through DOM tree until HTML or BODY tag is found. If
        doesn't find unique selector returns None.

        """
        cur_css_selector = u''
        _id = self.browser.get_id(element)

        if _id:
            cur_css_selector += u'#%s' % _id
        else:
            class_name = self.browser.get_class(element)
            if class_name:
                class_name = re.sub(r'\s+', '.', class_name)
                cur_css_selector += u'.%s' % class_name

        cur_el_tag = self.browser.get_tag_name(element)
        if cur_el_tag in ('body', 'html') or len(cur_css_selector) == 0:
            return None
        else:
            by_and_css_selector = By.CSS_SELECTOR, cur_css_selector
            elements_count = self.browser.get_elements_count(
                by_and_css_selector)
            if elements_count == 1:
                return by_and_css_selector
            else:
                parent = self.browser.get_parent(element)
                css_parent_selector = self._get_css_selector(parent)
                if css_parent_selector:
                    new_css_selector = u' > '.join(
                        (css_parent_selector[1], cur_css_selector))
                    return By.CSS_SELECTOR, new_css_selector
                else:
                    return None

    def _get_link_text_selector(self, element):
        text = self.browser.get_text(element)
        if len(self.browser.find_elements((By.LINK_TEXT, text))) == 1:
            return By.LINK_TEXT, text
        else:
            return None

    def _get_xpath_selector(self, element):
        return By.XPATH, self.browser.execute_js(self.GET_XPATH_USING_JS, element)
