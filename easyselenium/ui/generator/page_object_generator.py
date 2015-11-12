# coding=utf8
import os
import re
from time import sleep
from wx import Point, Rect

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from easyselenium.utils import unicode_str
from easyselenium.ui.root_folder import RootFolder
from easyselenium.ui.utils import get_py_file_name_from_class_name
from easyselenium.ui.generator.page_object_class import PageObjectClass, \
    PageObjectClassField
from easyselenium.ui.file_utils import check_if_path_exists


class PageObjectGenerator(object):
    # js code ref. -
    # https://code.google.com/p/fbug/source/browse/branches/firebug1.7/content/firebug/lib.js?r=8828
    # Next code was taken from Firebug project, credits to them
    # Check license file - ../../licenses/firebug_license.txt
    GET_XPATH_USING_JS = '''
function getElementXPath(element)
{
    if (element && element.id)
        return '//*[@id="' + element.id + '"]';
    else
        return getElementTreeXPath(element);
};

function getElementTreeXPath(element)
{
    var paths = [];

    // Use nodeName (instead of localName) so namespace prefix is included (if any).
    for (; element && element.nodeType == 1; element = element.parentNode)
    {
        var index = 0;
        for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling)
        {
            // Ignore document type declaration.
            if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE)
                continue;

            if (sibling.nodeName == element.nodeName)
                ++index;
        }

        var tagName = element.nodeName.toLowerCase();
        var pathIndex = (index ? "[" + (index+1) + "]" : "");
        paths.splice(0, 0, tagName + pathIndex);
    }

    return paths.length ? "/" + paths.join("/") : null;
};
return getElementXPath(arguments[0]);'''
    ELEMENTS_SELECTOR = (By.CSS_SELECTOR,
                         '[onclick], [jsaction], a, select, button, input, '
                         'span, p, h1, h2, h3, h4, h5, h6, '
                         'frame, iframe, .btn')
    FRAMES_SELECTOR = (By.CSS_SELECTOR, 'frame, iframe')

    def __init__(self, browser, logger=None):
        self.browser = browser
        self.logger = logger

    def __log(self, *msgs):
        if self.logger:
            self.logger.info(u" ".join([unicode_str(msg) for msg in msgs]))

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

    def __is_correct_element(self, element, area, location_offset):
        bad_element_tags = ['option', 'script']

        if area:
            if type(area) not in (tuple, list) or len(area) != 4:
                raise Exception(u"Bad area data '%s'" % str(area))
            area = Rect(*area)
            x, y = self.browser.get_location(element)
            if location_offset:
                # fixing location because it is located inside frame
                x += location_offset[0]
                y += location_offset[1]
            w, h = self.browser.get_dimensions(element)
            element_center = Point(x + w / 2, y + h / 2)
            is_element_inside = area.Contains(element_center)
        else:
            is_element_inside = True

        return (self.browser.is_visible(element) and
                not element.tag_name in bad_element_tags and
                is_element_inside)

    def __get_po_fields_from_page(self, area, location_offset=None):
        fields = []
        elements = self.browser.find_elements(self.ELEMENTS_SELECTOR)
        i = 1
        log_prefix = u' ' * 10
        for e in elements:
            self.__log(u'%5d/%d Trying to get PageObjectField for element %s' % (i,
                                                                                 len(elements),
                                                                                 self.browser._to_string(e)))
            if self.__is_correct_element(e, area, location_offset):
                field = self.__get_pageobject_field(e, location_offset)
                if field:
                    self.__log(log_prefix, u'PageObjectField:', field)
                    fields.append(field)
                else:
                    self.__log(log_prefix, u'Failed to unique selector')
            else:
                self.__log(log_prefix, u'Skipped - element is not supported/visible or is outside of area')
            i += 1

        self.__log(u'Number of fields:', len(fields))
        return fields

    def get_all_po_fields(self, url, area):
        if self.browser.get_current_url() != url:
            self.browser.get(url)
            sleep(3)

        fields = []
        self.browser.switch_to_default_content()
        self.__log(u'Getting fields for main content')
        fields += self.__get_po_fields_from_page(area)

        for frame in self.browser.find_elements(self.FRAMES_SELECTOR):
            self.browser.switch_to_default_content()
            location_offset = self.browser.get_location(frame)
            self.__log(u'Getting fields for frame', self.browser._to_string(frame))
            self.browser.switch_to_frame(frame)

            fields += self.__get_po_fields_from_page(area, location_offset)

        self.__log(u'Total number of fields:', len(fields))

        names = []
        for field in fields:
            if field.name in names:
                uniq_name = False
                i = 0
                while not uniq_name:
                    new_name = u'_'.join([field.name, str(i)])
                    if new_name not in names:
                        uniq_name = True
                        field.name = new_name
                    i += 1
            names.append(field.name)

        return fields

    def get_po_class_for_url(self, url, class_name, folder_path, area=None):
        po_folder = os.path.join(folder_path,
                                 RootFolder.PO_FOLDER)
        img_folder = os.path.join(folder_path,
                                  RootFolder.PO_FOLDER,
                                  PageObjectClass.IMAGE_FOLDER)
        check_if_path_exists(folder_path)

        self.__log(u'Generating PageObjectClass for url %s with area %s' % (url, str(area)))
        fields = self.get_all_po_fields(url, area)
        img_as_png = self.browser.get_screenshot_as_png()

        filename = get_py_file_name_from_class_name(class_name)
        file_path = os.path.join(po_folder, filename)
        img_path = os.path.join(img_folder,
                                os.path.splitext(filename)[0] + '.png')

        return PageObjectClass(class_name, url, fields,
                               area, file_path, img_path,
                               img_as_png)

    def __get_pageobject_field(self, element, location_offset):
        by_and_selector = self._get_selector(element)
        if by_and_selector:
            by, selector = by_and_selector

            name = self._get_name_for_field(by_and_selector)
            is_frame = self.browser.find_element(element).tag_name in ['frame', 'iframe']
            if is_frame:
                name = 'FRAME_' + name
            name_starts_with_number = re.match('^\d+.+$', name)
            if name_starts_with_number:
                name = u'N' + name

            location = self.browser.get_location(element)
            if location_offset:
                # fix location because it is inside frame
                location = location[0] + location_offset[0], location[1] + location_offset[1]
            dimensions = self.browser.get_dimensions(element)
            return PageObjectClassField(name, by,
                                        selector, location,
                                        dimensions)
        return None

    def _get_selector(self, element):
        for selector_func in (self._get_id_selector,
                              self._get_link_text_selector,
                              self._get_class_name_selector,
                              self._get_css_selector,
                              self._get_xpath_selector):
            if self.browser.is_visible(element):
                try:
                    by_and_selector = selector_func(element)
                    if by_and_selector:
                        return by_and_selector
                except Exception:
                    pass

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
        if (len(self.browser.find_elements((By.LINK_TEXT, text))) == 1 and
                    len(text) > 1):
            return By.LINK_TEXT, text
        else:
            return None

    def _get_xpath_selector(self, element):
        return By.XPATH, self.browser.execute_js(self.GET_XPATH_USING_JS, element)
