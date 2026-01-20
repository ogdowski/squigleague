"""Frontend tests for matchup creation and viewing using Selenium."""
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
def logged_in_browser(browser):
    """Create a logged-in browser session."""
    timestamp = int(time.time())
    user_data = {
        'email': f'matchuptest{timestamp}@example.com',
        'username': f'MatchupUser{timestamp}',
        'password': 'TestPassword123'
    }
    
    # Register user via API
    requests.post('http://localhost/api/auth/register', json=user_data)
    
    # Login via browser
    browser.get('http://localhost/login')
    
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    
    email_input = browser.find_element(By.CSS_SELECTOR, 'input[type="email"]')
    email_input.send_keys(user_data['email'])
    
    password_input = browser.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.send_keys(user_data['password'])
    
    submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    time.sleep(0.5)
    browser.execute_script("arguments[0].click();", submit_button)
    
    WebDriverWait(browser, 10).until(
        lambda d: d.current_url == 'http://localhost/'
    )
    
    return browser


class TestMatchupCreation:
    """Test matchup creation through the browser."""

    def test_create_matchup_authenticated(self, logged_in_browser):
        """Test that authenticated user can create a matchup."""
        browser = logged_in_browser
        
        browser.get('http://localhost/matchup/create')
        
        # Wait for army list textarea
        army_list_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input.send_keys('Test Army List\n- 20 units\n- Hero\n- Magic items')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should redirect to matchup page
        WebDriverWait(browser, 10).until(
            lambda d: '/matchup/' in d.current_url and d.current_url != 'http://localhost/matchup/create'
        )
        
        # Should see "Waiting" or similar status
        status_text = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Waiting') or contains(text(), 'waiting')]"))
        )
        assert status_text.is_displayed()

    def test_create_matchup_anonymous(self, browser):
        """Test that anonymous user can create a matchup."""
        browser.get('http://localhost/matchup/create')
        
        # Wait for army list textarea
        army_list_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input.send_keys('Anonymous Army List\n- 15 units\n- Leader')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Should redirect to matchup page
        WebDriverWait(browser, 10).until(
            lambda d: '/matchup/' in d.current_url and d.current_url != 'http://localhost/matchup/create'
        )
        
        # Should see status
        page_source = browser.page_source.lower()
        assert 'waiting' in page_source or 'submit' in page_source


class TestMatchupView:
    """Test viewing matchup details through the browser."""

    def test_view_matchup_status(self, logged_in_browser):
        """Test viewing matchup status page."""
        browser = logged_in_browser
        
        # Create a matchup first
        browser.get('http://localhost/matchup/create')
        
        army_list_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input.send_keys('View Test Army\n- Units\n- Heroes')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        # Wait for redirect
        WebDriverWait(browser, 10).until(
            lambda d: '/matchup/' in d.current_url and d.current_url != 'http://localhost/matchup/create'
        )
        
        matchup_url = browser.current_url
        
        # Page should display matchup information
        page_source = browser.page_source.lower()
        assert 'matchup' in page_source or 'waiting' in page_source
        
        # Should have share link or matchup name
        assert 'http' in browser.page_source or '/matchup/' in browser.page_source

    def test_submit_second_list(self, browser):
        """Test submitting the second player's list."""
        # Create matchup anonymously
        browser.get('http://localhost/matchup/create')
        
        army_list_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input.send_keys('Player 1 Army\n- Units')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        WebDriverWait(browser, 10).until(
            lambda d: '/matchup/' in d.current_url and d.current_url != 'http://localhost/matchup/create'
        )
        
        matchup_url = browser.current_url
        
        # Open in new "browser session" (clear cookies)
        browser.delete_all_cookies()
        browser.get(matchup_url)
        
        # Submit second army list
        army_list_input2 = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input2.send_keys('Player 2 Army\n- Different units')
        
        submit_button2 = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button2.click()
        
        time.sleep(2)
        
        # Should now show revealed matchup
        page_source = browser.page_source.lower()
        assert 'battle plan' in page_source or 'map' in page_source or 'revealed' in page_source


class TestBattlePlanDisplay:
    """Test battle plan display on revealed matchup."""

    def test_battle_plan_visible(self, browser):
        """Test that battle plan is displayed after both players submit."""
        # Create and complete a matchup
        browser.get('http://localhost/matchup/create')
        
        army_list_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input.send_keys('Army 1\n- Units')
        
        submit_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(0.5)
        browser.execute_script("arguments[0].click();", submit_button)
        
        WebDriverWait(browser, 10).until(
            lambda d: '/matchup/' in d.current_url
        )
        
        matchup_url = browser.current_url
        
        # Submit second list
        browser.delete_all_cookies()
        browser.get(matchup_url)
        
        army_list_input2 = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea'))
        )
        
        army_list_input2.send_keys('Army 2\n- Units')
        
        submit_button2 = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button2.click()
        
        time.sleep(2)
        
        # Check for battle plan elements
        page_source = browser.page_source.lower()
        
        # Should see battle plan name or image
        assert 'battle plan' in page_source or any(
            battleplan in page_source for battleplan in [
                'passing seasons', 'paths of the fey', 'roiling roots',
                'cyclic shifts', 'surge of slaughter', 'linked ley lines',
                'noxious nexus', 'liferoots', 'bountiful equinox',
                'lifecycle', 'creeping corruption', 'grasp of thorns'
            ]
        )
        
        # Should see objectives or scoring
        assert 'objectives' in page_source or 'scoring' in page_source
