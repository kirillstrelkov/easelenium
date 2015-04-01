# coding=utf8
from selenium.webdriver.common.by import By

from easyselenium.utils import unicode_str, get_match
from easyselenium.file_utils import safe_create_path, save_file
import os


def get_by_as_code_str(by):
    if by == By.LINK_TEXT:
        return u'By.LINK_TEXT'
    elif by == By.CLASS_NAME:
        return u'By.CLASS_NAME'
    elif by == By.CSS_SELECTOR:
        return u'By.CSS_SELECTOR'
    elif by == By.XPATH:
        return u'By.XPATH'
    elif by == By.ID:
        return u'By.ID'
    else:
        raise NotImplementedError


def get_by_from_code_str(by_as_string):
    if by_as_string == u'By.LINK_TEXT':
        return By.LINK_TEXT
    elif by_as_string == u'By.CLASS_NAME':
        return By.CLASS_NAME
    elif by_as_string == u'By.CSS_SELECTOR':
        return By.CSS_SELECTOR
    elif by_as_string == u'By.XPATH':
        return By.XPATH
    elif by_as_string == u'By.ID':
        return By.ID
    else:
        raise NotImplementedError


class PageObjectClassField(object):

    def __init__(self, name, by, selector, location, dimensions):
        self.name = name
        self.by = by
        self.selector = selector
        self.location = location
        self.dimensions = dimensions

    def __eq__(self, other):
        return (self.name == other.name and
                self.by == other.by and
                self.selector == other.selector)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return u'PageObjectClassField(%s)' % unicode_str(self.__dict__)


class PageObjectClass(object):
    IMAGE_FOLDER = 'img'
    TEMPLATE = u'''# coding=utf8
from selenium.webdriver.common.by import By


class {name}(object):
    # Please do NOT remove auto-generated comments
    # Url: {url}
    # Area: {area}
    # File path: {file_path}
    # Image path: {img_path}
{fields_as_code}

'''

    def __init__(self, name, url, fields,
                 area=None, file_path=None,
                 img_path=None, img_as_png=None):
        self.name = name
        self.url = url
        self.fields = fields
        self.area = area
        self.file_path = file_path
        self.img_as_png = img_as_png
        self.img_path = img_path

    def save(self, new_folder=None):
        if new_folder:
            py_filename = os.path.basename(self.file_path)
            img_filename = os.path.basename(self.img_path)
            self.file_path = os.path.abspath(os.path.join(new_folder,
                                                          py_filename))
            self.img_path = os.path.abspath(os.path.join(new_folder,
                                                         self.IMAGE_FOLDER,
                                                         img_filename))
        safe_create_path(self.file_path)
        safe_create_path(self.img_path)
        save_file(self.file_path, self._get_file_content())
        save_file(self.img_path, self.img_as_png, False)

    def _get_file_content(self):
        kwargs = self.__dict__.copy()
        kwargs[u'fields_as_code'] = self._get_fields_as_code()
        return self.TEMPLATE.format(**kwargs)

    def _get_fields_as_code(self):
        single_line = u"    {name} = ({by_as_code}, u'{selector}') # {comment}"
        lines = []
        for field in self.fields:
            lines.append(single_line.format(**{
                'name': field.name,
                'by_as_code': get_by_as_code_str(field.by),
                'selector': field.selector.replace("'", "\\'"),
                'comment': u'location: %s dimensions: %s' % (field.location,
                                                             field.dimensions)
            }))

        return u'\n'.join(lines)

    @classmethod
    def parse_string_to_po_class(cls, string):
        # class {name}(object):
        # Please do NOT remove auto-generated comments
        # Url: {url}
        # Area: {area}
        # Image path: {img_path}
        name_regexp = ur'class (\w+)\(object\):'
        url_regexp = ur'Url: (.+)'
        area_regexp = ur'Area: \(?([\w, ]+)\)?'
        img_path_regexp = ur'Image path: (.+)'
        file_path_regexp = ur'File path: (.+)'
        fields_regexp = ur'\s+(\w+) = (.+) # location: (.+) dimensions: (.+)'

        name = get_match(name_regexp, string)
        url = get_match(url_regexp, string)
        area = eval(get_match(area_regexp, string))
        img_path = get_match(img_path_regexp, string)
        file_path = get_match(file_path_regexp, string)
        tmp_fields = get_match(fields_regexp, string, False)
        fields = []

        for field_name, field_by_and_selector, field_location, field_dimensions in tmp_fields:
            by, selector = eval(field_by_and_selector)
            location = eval(field_location)
            dimensions = eval(field_dimensions)
            po_class_field = PageObjectClassField(
                field_name, by, selector, location, dimensions)
            fields.append(po_class_field)

        return PageObjectClass(name, url, fields, area, file_path, img_path)

    def __eq__(self, other):
        return (self.name == other.name and
                self.url == other.url and
                self.fields == other.fields and
                self.area == other.area and
                self.file_path == other.file_path and
                self.img_path == other.img_path)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return u'PageObjectClass(%s)' % unicode_str(self.__dict__)
