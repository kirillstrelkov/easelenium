"""Mouse."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement

    from easelenium.browser import Browser, TypeElement


class Mouse:
    """Mouse."""

    def __init__(self, browser: Browser) -> None:
        """Initialize."""
        self.browser = browser

    def left_click(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse left click."""
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

    def left_click_by_offset(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        xoffset: int = 0,
        yoffset: int = 0,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse left click with offset."""
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(  # noqa: SLF001
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

        self.browser._safe_log(  # noqa: SLF001
            "Click at '%s' by offset(%s,%s)",
            element,
            xoffset,
            yoffset,
        )

        actions.move_to_element(element).move_by_offset(
            xoffset,
            yoffset,
        ).click().perform()

    def hover(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse hover."""
        self.browser._safe_log("Hover at '%s'", element)  # noqa: SLF001

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

    def hover_by_offset(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        xoffset: int = 0,
        yoffset: int = 0,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse hover with offset."""
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(  # noqa: SLF001
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

        self.browser._safe_log(  # noqa: SLF001
            "Mouse over '%s' by offset(%s,%s)",
            element,
            xoffset,
            yoffset,
        )

        actions.move_to_element(element).move_by_offset(xoffset, yoffset).perform()

    def right_click(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse right click."""
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(  # noqa: SLF001
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

        self.browser._safe_log(  # noqa: SLF001
            "Right click at '%s'",
            element,
        )

        actions.context_click(element).perform()

    def right_click_by_offset(  # noqa: PLR0913
        self,
        element: TypeElement | WebElement | None = None,
        xoffset: int = 0,
        yoffset: int = 0,
        by_id: str | None = None,
        by_xpath: str | None = None,
        by_link: str | None = None,
        by_partial_link: str | None = None,
        by_name: str | None = None,
        by_tag: str | None = None,
        by_css: str | None = None,
        by_class: str | None = None,
    ) -> None:
        """Mouse right click with offset."""
        actions = self.browser.get_action_chains()
        element = self.browser._get_element(  # noqa: SLF001
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

        self.browser._safe_log(  # noqa: SLF001
            "Right click at '%s' by offset(%s,%s)",
            element,
            xoffset,
            yoffset,
        )

        actions.move_to_element(element).move_by_offset(
            xoffset,
            yoffset,
        ).context_click().perform()
