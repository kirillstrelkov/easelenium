from easelenium.browser import Browser


def is_headless(browser: Browser) -> bool:
    if browser.is_ff():
        return browser._driver.caps.get("moz:headless", False)

    if browser.is_gc():
        return "Headless" in browser.execute_js("return navigator.userAgent")

    raise NotImplementedError
