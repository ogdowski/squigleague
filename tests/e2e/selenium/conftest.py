import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


DEFAULT_BASE_URL = "http://localhost:8000"


def pytest_addoption(parser):
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run Selenium end-to-end tests",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("TEST_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for Selenium tests",
    )
    parser.addoption(
        "--browser",
        action="store",
        default=os.getenv("SELENIUM_BROWSER", "chrome"),
        help="Browser to use (chrome only)",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser headed instead of headless",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: End-to-end browser tests (Selenium)")
    if config.getoption("--run-e2e") and hasattr(config.option, "no_cov"):
        config.option.no_cov = True


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-e2e"):
        return

    skip_e2e = pytest.mark.skip(reason="e2e tests require --run-e2e")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def driver(pytestconfig):
    browser = pytestconfig.getoption("--browser").lower()
    headed = pytestconfig.getoption("--headed") or os.getenv("SELENIUM_HEADED") == "1"

    if browser != "chrome":
        raise pytest.UsageError("Only chrome browser is supported for now")

    options = Options()
    if not headed:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1366,768")

    service = ChromeService(ChromeDriverManager().install())
    browser_driver = webdriver.Chrome(service=service, options=options)
    browser_driver.implicitly_wait(5)

    yield browser_driver

    browser_driver.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)