"""Frontend tests for user registration using Selenium."""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


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


class TestRegistration:
    """Test user registration through the browser."""

    def test_successful_registration(self, browser):
        """Test that a user can successfully register."""
        browser.get('http://localhost/register')
        
        # Wait for page to load
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        # Fill in registration form
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(f'test{int(time.time())}@example.com')
        
        username_input = browser.find_element(By.CSS_SELECTOR, 'input[placeholder*="username" i]')
        username_input.send_keys(f'TestUser{int(time.time())}')
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('TestPassword123')
        
        # Submit form - use JavaScript click to avoid element interception
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)  # Brief wait for scroll
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Wait for redirect to home or success message
        WebDriverWait(browser, 10).until(
            lambda d: d.current_url == 'http://localhost/' or 
                     'successfully' in d.page_source.lower()
        )
        
        assert 'register' not in browser.current_url.lower()

    def test_registration_duplicate_email(self, browser):
        """Test that duplicate email registration fails."""
        # First registration
        browser.get('http://localhost/register')
        
        email = f'duplicate{int(time.time())}@example.com'
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(email)
        
        username_input = browser.find_element(By.CSS_SELECTOR, 'input[placeholder*="username" i]')
        username_input.send_keys(f'User{int(time.time())}')
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('TestPassword123')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        time.sleep(2)
        
        # Try to register again with same email
        browser.get('http://localhost/register')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(email)
        
        username_input = browser.find_element(By.CSS_SELECTOR, 'input[placeholder*="username" i]')
        username_input.send_keys(f'User{int(time.time()) + 1}')
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('TestPassword123')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should see error message
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="error" i], [class*="alert" i]'))
        )
        
        error_element = browser.find_element(By.CSS_SELECTOR, '[class*="error" i], [class*="alert" i]')
        assert 'already' in error_element.text.lower() or 'exists' in error_element.text.lower()

    def test_registration_short_password(self, browser):
        """Test that short password registration fails."""
        browser.get('http://localhost/register')
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
        )
        
        email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        email_input.send_keys(f'test{int(time.time())}@example.com')
        
        username_input = browser.find_element(By.CSS_SELECTOR, 'input[placeholder*="username" i]')
        username_input.send_keys(f'User{int(time.time())}')
        
        password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        password_input.send_keys('short')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should see error message
        time.sleep(1)
        
        error_message = browser.find_element(By.CSS_SELECTOR, '[class*="error" i], [class*="alert" i]')
        assert error_message.is_displayed()
        assert '8' in error_message.text or 'characters' in error_message.text.lower()
