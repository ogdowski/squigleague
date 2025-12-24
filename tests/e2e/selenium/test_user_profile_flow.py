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


def login(driver, wait: WebDriverWait, base_url: str) -> None:
    driver.get(build_url(base_url, LOGIN_PATH))

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']")))
    driver.find_element(By.CSS_SELECTOR, "input[type='text']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").clear()
    driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(
        lambda d: "/squire/login" not in d.current_url
        or d.execute_script("return window.localStorage.getItem('auth_token')")
    )


def open_user_menu(driver, wait: WebDriverWait) -> None:
    trigger = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[x-show='isLoggedIn'] button"))
    )
    trigger.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isLoggedIn']")))


def test_user_menu_visible_after_login(driver, wait, base_url):
    login(driver, wait, base_url)
    driver.get(build_url(base_url, "/"))

    user_menu_button = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isLoggedIn'] button"))
    )
    assert user_menu_button.is_displayed()

    login_links_hidden = EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='!isLoggedIn']"))
    assert login_links_hidden(driver)


def test_navigate_to_profile_page(driver, wait, base_url):
    login(driver, wait, base_url)
    open_user_menu(driver, wait)

    profile_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/squire/profile']"))
    )
    profile_link.click()
    wait.until(EC.url_contains("/squire/profile"))

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1")))
    profile_heading = driver.find_element(By.CSS_SELECTOR, "h1")
    assert "User Profile" in profile_heading.text

    username_el = wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//p[contains(@class, 'font-semibold') and contains(normalize-space(), 'alakkhaine')]",
            )
        )
    )
    assert username_el.is_displayed()


def test_navigate_to_history_page(driver, wait, base_url):
    login(driver, wait, base_url)
    open_user_menu(driver, wait)

    history_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/squire/history']"))
    )
    history_link.click()
    wait.until(EC.url_contains("/squire/history"))

    heading = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1")))
    assert "Matchup History" in heading.text


def test_navigate_to_settings_page(driver, wait, base_url):
    login(driver, wait, base_url)
    open_user_menu(driver, wait)

    settings_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/squire/settings']"))
    )
    settings_link.click()
    wait.until(EC.url_contains("/squire/settings"))

    heading = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1")))
    assert "Account Settings" in heading.text


def test_logout_clears_session(driver, wait, base_url):
    login(driver, wait, base_url)
    open_user_menu(driver, wait)

    logout_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(), 'Logout')"]))
    )
    logout_button.click()

    wait.until(
        lambda d: "/squire/login" in d.current_url or d.current_url.rstrip("/") == base_url
    )

    login_link = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a[href='/squire/login']"))
    )
    assert login_link.is_displayed()

    user_menu_hidden = EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='isLoggedIn']"))
    assert user_menu_hidden(driver)

    token = driver.execute_script("return window.localStorage.getItem('auth_token')")
    assert not token