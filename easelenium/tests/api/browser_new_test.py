# coding=utf8

from easelenium.base_test import BaseTest


class BrowserTest(BaseTest):
    BROWSER_NAME = "gc"

    def test_get_parent(self):
        self.browser.get("https://duckduckgo.com/")
        element = self.browser.find_element(by_id="content_homepage")

        parent_tags = set()
        for _ in range(3):
            element = self.browser.get_parent(element)
            parent_tags.add(element.tag_name)

        assert "body" in parent_tags

    def test_switch_to_frame(self):
        frame = "iframe[src*=default]"

        url = "https://www.w3schools.com/html/html_iframe.asp"
        frame_url = "https://www.w3schools.com/html/default.asp"

        self.browser.get(url)
        assert url == self.browser.get_current_frame_url()

        self.browser.switch_to_frame(by_css=frame)
        assert frame_url == self.browser.get_current_frame_url()

        self.browser.switch_to_default_content()
        assert url == self.browser.get_current_frame_url()

    def test_type_click_get_text(self):
        self.browser.get("https://duckduckgo.com/")

        text_field = "search_form_input_homepage"
        search_btn = "search_button_homepage"
        results = "#links a.result__a"

        self.browser.type(by_id=text_field, text="selenium python docs")
        self.browser.click(by_id=search_btn)

        self.browser.wait_for_visible(by_css=results)
        assert "Selenium with Python" in self.browser.get_text(by_css=results)

    def test_mouse_left_right_clicks(self):
        self.browser.get("https://www.openstreetmap.org/")

        map_element = "map"
        context_menu = "#map .leaflet-contextmenu"
        welcome_close = ".welcome.visible .geolink .close"

        self.browser.wait_for_visible(by_css=welcome_close)

        assert not self.browser.is_visible(by_css=context_menu)
        if self.browser.is_visible(by_css=welcome_close):
            self.browser.click(by_css=welcome_close)

        self.browser.mouse.right_click(by_id=map_element)
        self.browser.wait_for_visible(by_css=context_menu)

        self.browser.mouse.left_click_by_offset(
            xoffset=-50, yoffset=-50, by_id=map_element
        )
        self.browser.wait_for_not_visible(by_css=context_menu)

        self.browser.mouse.right_click_by_offset(
            xoffset=100, yoffset=100, by_id=map_element
        )
        self.browser.wait_for_visible(by_css=context_menu)

    def test_mouse_hover(self):
        self.browser.get("https://www.openstreetmap.org/")

        edit_buton = "editanchor"
        tooltip = ".tooltip-inner"

        self.browser.mouse.hover(by_id=edit_buton)
        self.browser.wait_for_visible(by_css=tooltip)
        assert "Zoom in to edit the map" == self.browser.get_text(by_css=tooltip)

    def test_select(self):
        self.browser.get(
            "https://mdn.mozillademos.org/en-US/docs/Web/HTML/Element/select$samples/Basic_select?revision=1620423"
        )

        select_element = "select[name]"

        old_option = self.browser.get_selected_text_from_dropdown(by_css=select_element)
        self.browser.select_random_option_from_dropdown(
            by_css=select_element, texts_to_skip=[old_option]
        )
        new_option = self.browser.get_selected_text_from_dropdown(by_css=select_element)
        new_option_value = self.browser.get_selected_value_from_dropdown(
            by_css=select_element
        )

        assert old_option != new_option
        assert new_option.lower().split(" ")[0] == new_option_value

        self.browser.select_option_by_index_from_dropdown(
            by_css=select_element, index=0
        )

        new_option = "Second Value"
        self.browser.select_option_by_text_from_dropdown(
            by_css=select_element, text=new_option
        )
        assert (
            self.browser.get_selected_text_from_dropdown(by_css=select_element)
            == new_option
        )

        new_option = "third"
        self.browser.select_option_by_value_from_dropdown(
            by_css=select_element, value=new_option
        )
        assert (
            self.browser.get_selected_value_from_dropdown(by_css=select_element)
            == new_option
        )

        index = 0
        self.browser.select_option_by_index_from_dropdown(
            by_css=select_element, index=index
        )
        assert (
            self.browser.get_selected_value_from_dropdown(by_css=select_element)
            == "first"
        )
        index = 2
        self.browser.select_option_by_index_from_dropdown(
            by_css=select_element, index=index
        )
        assert (
            self.browser.get_selected_value_from_dropdown(by_css=select_element)
            == "third"
        )

        texts = self.browser.get_texts_from_dropdown(by_css=select_element)
        values = self.browser.get_values_from_dropdown(by_css=select_element)
        assert len(texts) == len(values)
        assert texts == [u"First Value", "Second Value", "Third Value"]
        assert values == [u"first", "second", "third"]

    def test_js_script(self):
        self.browser.get("https://duckduckgo.com/")
        js_statement = "return document.getElementsByClassName('badge-link__title')[0].textContent;"
        value = self.browser.execute_js(js_statement)

        assert "We can help" in value

    def test_open_close_new_window(self):
        self.browser.get("https://html.com/attributes/a-target/")

        a_element = 'a[target="_blank"]'

        title_before_click = self.browser.get_title()
        self.browser.switch_to_new_window(self.browser.click, by_css=a_element)
        title_after_click = self.browser.get_title()

        assert title_before_click != title_after_click

        self.browser.close_current_window_and_focus_to_previous_one()
        title_after_close = self.browser.get_title()
        assert title_before_click == title_after_close

    def test_alerts(self):
        self.browser.get("https://duckduckgo.com/")
        js_statement = "window.alert_val = window.confirm('Confirm dialog');"

        self.browser.execute_js(js_statement)
        self.browser.alert_accept()
        assert self.browser.execute_js("return window.alert_val;")

        self.browser.execute_js(js_statement)
        self.browser.alert_dismiss()
        assert not self.browser.execute_js("return window.alert_val;")
