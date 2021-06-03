class Mouse(object):
    def __init__(self, browser):
        self.browser = browser

    def left_click(
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
        self.left_click_by_offset(
            element,
            0,
            0,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def left_click_by_offset(
        self,
        element=None,
        xoffset=0,
        yoffset=0,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(
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
        self.browser.wait_for_visible(
            element=element,
        )

        if type(element) == tuple:
            element = self.browser.find_element(
                element=element,
            )

        self.browser._safe_log(
            "Click at '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(
            xoffset, yoffset
        ).click().perform()

    def hover(
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
        self.browser._safe_log("Hover at '%s'", element)

        self.hover_by_offset(
            element,
            0,
            0,
            by_id=by_id,
            by_xpath=by_xpath,
            by_link=by_link,
            by_partial_link=by_partial_link,
            by_name=by_name,
            by_tag=by_tag,
            by_css=by_css,
            by_class=by_class,
        )

    def hover_by_offset(
        self,
        element=None,
        xoffset=0,
        yoffset=0,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(
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
        self.browser.wait_for_visible(
            element=element,
        )

        element = self.browser.find_element(
            element=element,
        )

        self.browser._safe_log(
            "Mouse over '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(xoffset, yoffset).perform()

    def right_click(
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
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(
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
        self.browser.wait_for_visible(
            element=element,
        )

        if type(element) == tuple:
            element = self.browser.find_element(
                element=element,
            )

        self.browser._safe_log(
            "Right click at '%s'",
            self.browser._to_string(
                element=element,
            ),
        )

        actions.context_click(element).perform()

    def right_click_by_offset(
        self,
        element=None,
        xoffset=0,
        yoffset=0,
        by_id=None,
        by_xpath=None,
        by_link=None,
        by_partial_link=None,
        by_name=None,
        by_tag=None,
        by_css=None,
        by_class=None,
    ):
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(
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
        self.browser.wait_for_visible(
            element=element,
        )

        if type(element) == tuple:
            element = self.browser.find_element(
                element=element,
            )

        self.browser._safe_log(
            "Right click at '%s' by offset(%s,%s)", element, xoffset, yoffset
        )

        actions.move_to_element(element).move_by_offset(
            xoffset, yoffset
        ).context_click().perform()
