import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


pytestmark = [pytest.mark.e2e]

LOGIN_PATH = "/squire/login"
USERNAME = "alakkhaine"
PASSWORD = "FinFan11"


def build_url(base_url: str, path: str) -> str:
    return f"{base_url}{path}"


def open_login(driver, wait: WebDriverWait, base_url: str) -> None:
    driver.get(build_url(base_url, LOGIN_PATH))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))


def fill_credentials(driver, username: str, password: str) -> None:
    username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    username_input.clear()
    password_input.clear()

    username_input.send_keys(username)
    password_input.send_keys(password)


def submit_login(driver) -> None:
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def test_login_form_renders(driver, wait, base_url):
    open_login(driver, wait, base_url)

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))


def test_invalid_credentials_shows_error(driver, wait, base_url):
    open_login(driver, wait, base_url)
    fill_credentials(driver, USERNAME, "WrongPassword123")
    submit_login(driver)

    error_selector = (By.CSS_SELECTOR, "[x-show='error'] [x-text='error']")
    error_element = wait.until(EC.visibility_of_element_located(error_selector))
    error_text = error_element.text.strip()

    assert error_text, "Expected an error message to be displayed"
    assert error_text != "[object Object]", "Error message should be human readable"
    assert "invalid" in error_text.lower(), "Should mention invalid credentials"


def test_valid_login_redirects_or_stores_token(driver, wait, base_url):
    open_login(driver, wait, base_url)
    fill_credentials(driver, USERNAME, PASSWORD)
    submit_login(driver)

    wait.until(
        lambda d: "/squire/login" not in d.current_url
        or d.execute_script("return window.localStorage.getItem('auth_token')")
    )

    token = driver.execute_script("return window.localStorage.getItem('auth_token')")
    on_login_page = "/squire/login" in driver.current_url

    assert token or not on_login_page, "Expected redirect or stored auth token after login"