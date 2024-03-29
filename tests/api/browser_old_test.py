"""Old Browser API tests."""

from selenium.webdriver.common.by import By

from easelenium.base_test import BaseTest


class BrowserTest(BaseTest):
    """Browser tests."""

    BROWSER_NAME = "gc"

    def test_switch_to_frame(self) -> None:
        """Check switch to frame."""
        frame = (By.CSS_SELECTOR, "iframe[src*=default]")

        url = "https://www.w3schools.com/html/html_iframe.asp"
        frame_url = "https://www.w3schools.com/html/default.asp"

        self.browser.get(url)
        assert url == self.browser.get_current_frame_url()

        self.browser.switch_to_frame(frame)
        assert frame_url == self.browser.get_current_frame_url()

        self.browser.switch_to_default_content()
        assert url == self.browser.get_current_frame_url()

    def test_type_click_get_text(self) -> None:
        """Check type, click, get text."""
        self.browser.get("https://duckduckgo.com/")

        text_field = (By.ID, "searchbox_input")
        search_btn = (By.CSS_SELECTOR, "[aria-label='Search']")
        results = (By.CSS_SELECTOR, "article")

        self.browser.type(text_field, "selenium python io")
        self.browser.click(search_btn)

        self.browser.wait_for_visible(results)
        assert "Selenium with Python" in self.browser.get_text(results)

    def test_mouse_left_right_clicks(self) -> None:
        """Check mouse left and right clicks."""
        self.browser.get("https://www.openstreetmap.org/")

        map_element = (By.ID, "map")
        context_menu = (By.CSS_SELECTOR, "#map .leaflet-contextmenu")
        welcome_close = (By.CSS_SELECTOR, ".welcome .btn-close")

        self.browser.wait_for_visible(welcome_close)

        assert not self.browser.is_visible(context_menu)
        if self.browser.is_visible(welcome_close):
            self.browser.click(welcome_close)

        self.browser.mouse.right_click(map_element)
        self.browser.wait_for_visible(context_menu)

        self.browser.mouse.left_click_by_offset(map_element, -50, -50)
        self.browser.wait_for_not_visible(context_menu)

        self.browser.mouse.right_click_by_offset(map_element, 100, 100)
        self.browser.wait_for_visible(context_menu)

    def test_mouse_hover(self) -> None:
        """Check mouse hover."""
        self.browser.get("https://www.openstreetmap.org/")

        edit_buton = (By.CSS_SELECTOR, ".control-button.zoomin")
        tooltip = (By.CSS_SELECTOR, ".tooltip")

        self.browser.mouse.hover(edit_buton)
        self.browser.wait_for_visible(tooltip)
        assert self.browser.get_text(tooltip) == "Zoom In"

    def test_select(self) -> None:
        """Check select."""
        self.browser.get(
            "https://yari-demos.prod.mdn.mozit.cloud/en-US/docs/Web/HTML/Element/select/_sample_.Basic_select.html",
        )

        select_element = (By.CSS_SELECTOR, "select[name]")

        old_option = self.browser.get_selected_text_from_dropdown(select_element)
        self.browser.select_random_option_from_dropdown(
            select_element,
            texts_to_skip=(old_option,),
        )
        new_option = self.browser.get_selected_text_from_dropdown(select_element)
        new_option_value = self.browser.get_selected_value_from_dropdown(select_element)

        assert old_option != new_option
        assert new_option.lower().split(" ")[0] == new_option_value

        self.browser.select_option_by_index_from_dropdown(select_element, 0)

        new_option = "Second Value"
        self.browser.select_option_by_text_from_dropdown(select_element, new_option)
        assert (
            self.browser.get_selected_text_from_dropdown(select_element) == new_option
        )

        new_option = "third"
        self.browser.select_option_by_value_from_dropdown(select_element, new_option)
        assert (
            self.browser.get_selected_value_from_dropdown(select_element) == new_option
        )

        index = 0
        self.browser.select_option_by_index_from_dropdown(select_element, index)
        assert self.browser.get_selected_value_from_dropdown(select_element) == "first"
        index = 2
        self.browser.select_option_by_index_from_dropdown(select_element, index)
        assert self.browser.get_selected_value_from_dropdown(select_element) == "third"

        texts = self.browser.get_texts_from_dropdown(select_element)
        values = self.browser.get_values_from_dropdown(select_element)
        assert len(texts) == len(values)
        assert texts == ["First Value", "Second Value", "Third Value"]
        assert values == ["first", "second", "third"]

    def test_js_script(self) -> None:
        """Check JavaScript execution."""
        self.browser.get("https://duckduckgo.com/")
        js_statement = "return document.getElementsByTagName('h2')[0].textContent;"
        value = self.browser.execute_js(js_statement)

        assert "We can help" in value

    def test_open_close_new_window(self) -> None:
        """Check open and close new window."""
        self.browser.get("https://html.com/attributes/a-target/")

        a_element = (By.CSS_SELECTOR, 'a[target="_blank"]')

        title_before_click = self.browser.get_title()
        self.browser.switch_to_new_window(self.browser.click, a_element)
        title_after_click = self.browser.get_title()

        assert title_before_click != title_after_click

        self.browser.close_current_window_and_focus_to_previous_one()
        title_after_close = self.browser.get_title()
        assert title_before_click == title_after_close

    def test_alerts(self) -> None:
        """Check alerts."""
        self.browser.get("https://duckduckgo.com/")
        js_statement = "window.alert_val = window.confirm('Confirm dialog');"

        self.browser.execute_js(js_statement)
        self.browser.alert_accept()
        assert self.browser.execute_js("return window.alert_val;")

        self.browser.execute_js(js_statement)
        self.browser.alert_dismiss()
        assert not self.browser.execute_js("return window.alert_val;")

    def test_get_attribute(self) -> None:
        """Check get attribute."""
        self.browser.get("https://duckduckgo.com/")
        assert (
            self.browser.get_attribute(
                (By.CSS_SELECTOR, "a[class*='header_logoHorizontal']"),
                "href",
            )
            == "https://duckduckgo.com/about"
        )

    def test_get_attribute_with_parent(self) -> None:
        """Check get attribute with parent."""
        self.browser.get("https://duckduckgo.com/")
        parent = self.browser.find_element(by_tag="main")
        assert (
            self.browser.get_attribute(
                (By.CSS_SELECTOR, "a[class*='header_logoHorizontal']"),
                "href",
                parent=parent,
            )
            == "https://duckduckgo.com/about"
        )
