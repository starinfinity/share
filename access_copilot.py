import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class GitHubCopilotScraper:
    def __init__(self, username, password):
        """
        Initialize the scraper with GitHub credentials
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.driver = None

    def setup_selenium_driver(self):
        """
        Set up Selenium WebDriver for browser automation
        """
        # Chrome options for headless browsing
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Setup Chrome WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def login_to_github(self):
        """
        Perform login to GitHub using Selenium
        """
        if not self.driver:
            self.setup_selenium_driver()

        try:
            # Navigate to GitHub login page
            self.driver.get("https://github.com/login")

            # Find and fill in username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_field"))
            )
            username_field.send_keys(self.username)

            # Find and fill in password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.NAME, "commit")
            login_button.click()

            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("github.com")
            )

            print("Successfully logged into GitHub")
            return True

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def access_copilot_chat(self):
        """
        Navigate to Copilot Chat interface
        """
        if not self.driver:
            print("Please login first")
            return None

        try:
            # Navigate to Copilot Chat
            self.driver.get("https://github.com/github-copilot/chat")

            # Wait for Copilot Chat to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "copilot-chat-interface"))
            )

            # Get page source for parsing
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            return soup

        except Exception as e:
            print(f"Failed to access Copilot Chat: {e}")
            return None

    def send_message(self, message):
        """
        Send a message in Copilot Chat
        """
        try:
            # Find message input field
            message_input = self.driver.find_element(By.CLASS_NAME, "chat-input-textarea")
            message_input.send_keys(message)

            # Find and click send button
            send_button = self.driver.find_element(By.CLASS_NAME, "send-button")
            send_button.click()

            # Wait for response
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ai-response"))
            )

            # Retrieve response
            response_element = self.driver.find_element(By.CLASS_NAME, "ai-response")
            return response_element.text

        except Exception as e:
            print(f"Failed to send message: {e}")
            return None

    def close(self):
        """
        Close the browser session
        """
        if self.driver:
            self.driver.quit()

def main():
    # Get credentials from environment variables
    USERNAME = os.environ.get('GITHUB_USERNAME')
    PASSWORD = os.environ.get('GITHUB_PASSWORD')

    if not USERNAME or not PASSWORD:
        print("Please set GITHUB_USERNAME and GITHUB_PASSWORD environment variables")
        return

    # Initialize scraper
    scraper = GitHubCopilotScraper(USERNAME, PASSWORD)

    try:
        # Login to GitHub
        if scraper.login_to_github():
            # Access Copilot Chat
            copilot_soup = scraper.access_copilot_chat()
            
            if copilot_soup:
                # Send a test message
                response = scraper.send_message("Write a Python function to calculate Fibonacci sequence")
                print("Copilot Response:", response)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Always close the browser
        scraper.close()

if __name__ == '__main__':
    main()
