"""Frontend tests for user login using Selenium."""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests


@pytest.fixture
def browser():
    """Create a Chrome browser instance."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture
def test_user():
    """Create a test user via API."""
    timestamp = int(time.time())
    user_data = {
        'email': f'logintest{timestamp}@example.com',
        'username': f'LoginUser{timestamp}',
        'password': 'TestPassword123'
    }
    
    response = requests.post(
        'http://localhost/api/auth/register',
        json=user_data
    )
    assert response.status_code == 201
    
    return user_data


class TestLogin:
    """Test user login through the browser."""

    def test_successful_login(self, browser, test_user):
        """Test that a user can successfully log in."""
        browser.get('http://localhost/login')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(test_user['email'])
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should redirect to home page
        WebDriverWait(browser, 10).until(
            lambda d: d.current_url == 'http://localhost/'
        )
        
        # Should see username in nav
        username_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{test_user['username']}')]"))
        )
        assert username_element.is_displayed()

    def test_login_wrong_password(self, browser, test_user):
        """Test that login fails with wrong password."""
        browser.get('http://localhost/login')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(test_user['email'])
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('WrongPassword123')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should see error message
        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="error" i], [class*="alert" i]'))
        )
        assert error_message.is_displayed()
        assert 'failed' in error_message.text.lower() or 'invalid' in error_message.text.lower()

    def test_login_nonexistent_user(self, browser):
        """Test that login fails for nonexistent user."""
        browser.get('http://localhost/login')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(f'nonexistent{int(time.time())}@example.com')
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('SomePassword123')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should see error message
        error_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="error" i], [class*="alert" i]'))
        )
        assert error_message.is_displayed()
        assert 'failed' in error_message.text.lower() or 'invalid' in error_message.text.lower()

    def test_logout(self, browser, test_user):
        """Test that user can log out."""
        # First login
        browser.get('http://localhost/login')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(test_user['email'])
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys(test_user['password'])
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        WebDriverWait(browser, 10).until(
            lambda d: d.current_url == 'http://localhost/'
        )
        
        # Click logout button
        logout_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Logout')]"))
        )
        logout_button.click()
        
        time.sleep(1)
        
        # Should see Login button again
        login_link = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/login')]"))
        )
        assert login_link.is_displayed()
