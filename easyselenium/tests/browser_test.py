# coding=utf8
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from easyselenium.base_test import BaseTest


class BrowserTest(BaseTest):
    LOGGER = False

    def test_switch_to_frame(self):
        frame_left = (By.XPATH, "//frame[@name='menu']")

        url = 'http://www.quackit.com/html/templates/' + \
              'frames/frames_example_1.html'
        frame_url = 'http://www.quackit.com/html/templates/frames/menu_1.html'

        self.browser.get(url)
        self.assertEqual(url, self.browser.get_current_url())

        self.browser.switch_to_frame(frame_left)
        self.assertEqual(frame_url, self.browser.get_current_url())

        self.browser.switch_to_default_content()
        self.assertEqual(url, self.browser.get_current_url())

    def test_type_click_get_text(self):
        self.browser.get('https://duckduckgo.com/')

        text_field = (By.ID, 'search_form_input_homepage')
        search_btn = (By.ID, 'search_button_homepage')
        results = (By.CSS_SELECTOR, '#links a.result__a')

        self.browser.type(text_field, 'selenium')
        self.browser.click(search_btn)

        self.assertEqual('Selenium - Web Browser Automation',
                         self.browser.get_text(results))

    def test_mouse_left_right_clicks(self):
        self.browser.get('http://maps.skobbler.co.uk/')

        map_element = (By.CSS_SELECTOR, '#map .leaflet-tile-pane')
        context_menu = (By.ID, 'context-menu')

        # removes'Share your location' browser's message
        self.browser.type(map_element, Keys.ESCAPE)

        self.assertFalse(self.browser.is_visible(context_menu))

        self.browser.mouse.right_click(map_element)
        self.browser.wait_for_visible(context_menu)

        self.browser.mouse.left_click(map_element)
        self.browser.wait_for_not_visible(context_menu)

        self.browser.mouse.right_click_by_offset(map_element, 200, 200)
        self.browser.wait_for_visible(context_menu)

    def test_mouse_hover(self):
        self.browser.get('http://maps.skobbler.co.uk/')

        favourites = (By.CSS_SELECTOR, "a[rel='favorites-menu']")
        favourites_tooptip = (By.ID, 'favorites-menu-tip')

        self.browser.mouse.hover(favourites)
        self.browser.wait_for_visible(favourites_tooptip)

    def test_select(self):
        self.browser.get('https://developer.mozilla.org/en-US/docs/' +
                         'Web/HTML/Element/select')

        select_element = (By.CSS_SELECTOR, "select[name='select']")

        old_option = self.browser.get_selected_text_of_dropdown(select_element)
        self.browser.select_random_option_from_dropdown(select_element,
                                                        old_option)
        new_option = self.browser.get_selected_text_of_dropdown(select_element)
        new_option_value = self.browser\
            .get_selected_value_of_dropdown(select_element)

        self.assertNotEqual(old_option, new_option)
        self.assertEqual(new_option.lower().replace(' ', ''), new_option_value)

        self.browser.select_option_by_index_from_dropdown(select_element, 0)

        new_option = 'Value 2'
        self.browser.select_option_by_text_from_dropdown(select_element,
                                                         new_option)
        self.assertEqual(
            self.browser.get_selected_text_of_dropdown(select_element),
            new_option
        )

        new_option = 'value3'
        self.browser.select_option_by_value_from_dropdown(select_element,
                                                          new_option)
        self.assertEqual(
            self.browser.get_selected_value_of_dropdown(select_element),
            new_option
        )

        index = 0
        self.browser.select_option_by_index_from_dropdown(
            select_element, index)
        self.assertEquals(
            self.browser.get_selected_value_of_dropdown(select_element),
            'value%d' % (index + 1)
        )

        index = 2
        self.browser.select_option_by_index_from_dropdown(
            select_element, index)
        self.assertEquals(
            self.browser.get_selected_value_of_dropdown(select_element),
            'value%d' % (index + 1)
        )

        texts = self.browser.get_texts_from_dropdown(select_element)
        values = self.browser.get_values_from_dropdown(select_element)
        self.assertEqual(len(texts), len(values))
        self.assertEqual(texts, ['Value %d' % i for i in range(1, 4)])
        self.assertEqual(values, ['value%d' % i for i in range(1, 4)])

    def test_js_script(self):
        self.browser.get('https://duckduckgo.com/')
        js_statement = "return document.getElementsByClassName('tag-home')[0]"\
                       '.textContent;'
        value = self.browser.execute_js(js_statement)

        self.assertIn(
            "The search engine that doesn't track you.", value.strip())

    def test_open_close_new_window(self):
        self.browser.get('https://mdn.mozillademos.org/en-US/docs/Web/HTML/'
                         'Element/a$samples/Example.3A_Creating_a_clickable_image')

        a_element = (By.CSS_SELECTOR, 'a[target="_blank"]')

        title_before_click = self.browser.get_title()
        self.browser.switch_to_new_window(self.browser.click, a_element)
        title_after_click = self.browser.get_title()

        self.assertNotEqual(title_before_click, title_after_click)

        self.browser.close_current_window_and_focus_to_previous_one()
        title_after_close = self.browser.get_title()
        self.assertEqual(title_before_click, title_after_close)

    def test_alerts(self):
        self.browser.get('https://duckduckgo.com/')
        js_statement = "value = window.confirm('Confirm dialog');"

        self.browser.execute_js(js_statement)
        self.browser.alert_accept()
        self.assertTrue(self.browser.execute_js('return value;'))

        self.browser.execute_js(js_statement)
        self.browser.alert_dismiss()
        self.assertFalse(self.browser.execute_js('return value;'))
