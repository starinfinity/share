import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configure logging
def setup_logger():
    """
    Set up a comprehensive logging configuration
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Configure logging to write to both file and console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # Log to console
            logging.StreamHandler(),
            # Log to file with timestamp
            logging.FileHandler(f'logs/github_copilot_edge_scraper_{int(time.time())}.log')
        ]
    )
    return logging.getLogger(__name__)


class GitHubCopilotScraper:
    def __init__(self, username, password):
        """
        Initialize the scraper with GitHub credentials
        """
        # Setup logger
        self.logger = setup_logger()

        self.username = username
        self.password = password
        self.driver = None

    def setup_selenium_driver(self):
        """
        Set up Selenium WebDriver using Microsoft Edge
        """
        try:
            self.logger.info("Setting up Microsoft Edge WebDriver...")

            # Edge options
            edge_options = Options()
            # Uncomment to run in background
            # edge_options.add_argument("--headless")

            # Setup Edge WebDriver
            self.driver = webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install()),
                options=edge_options
            )

            # Set implicit wait to help with element detection
            self.driver.implicitly_wait(10)

            self.logger.info("Microsoft Edge WebDriver setup complete")
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            raise

    def login_to_github(self):
        """
        Perform login to GitHub using Selenium with detailed logging
        """
        try:
            # Setup driver if not already done
            if not self.driver:
                self.setup_selenium_driver()

            # Navigate to login page
            self.logger.info("Navigating to GitHub login page...")
            self.driver.get("https://github.com/login")

            # Log login attempt details
            self.logger.info(f"Attempting to log in with username: {self.username}")

            # Find and fill username
            username_field = self.driver.find_element(By.ID, "login_field")
            username_field.send_keys(self.username)
            self.logger.info("Username entered successfully")

            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            self.logger.info("Password entered successfully")

            # Click login button
            login_button = self.driver.find_element(By.NAME, "commit")
            login_button.click()
            self.logger.info("Login button clicked")

            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("github.com")
            )
            self.logger.info("Successfully logged into GitHub")

            # Optional: Take screenshot of logged-in page
            screenshot_path = f'logs/github_login_{int(time.time())}.png'
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Login page screenshot saved to {screenshot_path}")

            return True

        except TimeoutException:
            self.logger.error("Timeout waiting for login to complete")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Element not found during login: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {e}")
            return False

    def access_copilot_chat(self):
        """
        Navigate to Copilot Chat interface with logging
        """
        try:
            self.logger.info("Attempting to access Copilot Chat...")

            # Navigate to Copilot Chat
            self.driver.get("https://github.com/github-copilot/chat")

            self.logger.info("Navigated to Copilot Chat page")

            # Optional: Wait for specific element to confirm page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "copilot-chat-interface"))
            )

            self.logger.info("Copilot Chat interface loaded successfully")

            # Optional: Take screenshot of Copilot Chat page
            screenshot_path = f'logs/copilot_chat_{int(time.time())}.png'
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Copilot Chat page screenshot saved to {screenshot_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to access Copilot Chat: {e}")
            return False

    def send_message(self, message):
        """
        Send a message in Copilot Chat with comprehensive logging
        """
        try:
            self.logger.info(f"Preparing to send message: {message}")

            # Find message input field
            message_input = self.driver.find_element(By.CLASS_NAME, "chat-input-textarea")
            message_input.send_keys(message)
            self.logger.info("Message entered into input field")

            # Find and click send button
            send_button = self.driver.find_element(By.CLASS_NAME, "send-button")
            send_button.click()
            self.logger.info("Send button clicked")

            # Wait for response
            response_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ai-response"))
            )

            # Log response
            response_text = response_element.text
            self.logger.info("Response received successfully")
            self.logger.info(f"Response: {response_text}")

            return response_text

        except Exception as e:
            self.logger.error(f"Failed to send message or receive response: {e}")
            return None

    def close(self):
        """
        Close the browser session with logging
        """
        try:
            if self.driver:
                self.logger.info("Closing browser session...")
                self.driver.quit()
                self.logger.info("Browser session closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")


def main():
    # Get credentials from environment variables
    USERNAME = "abc"
    PASSWORD = "abc"

    # Setup logger for main function
    logger = logging.getLogger(__name__)

    if not USERNAME or not PASSWORD:
        logger.error("Please set GITHUB_USERNAME and GITHUB_PASSWORD environment variables")
        return

    # Initialize scraper
    scraper = GitHubCopilotScraper(USERNAME, PASSWORD)

    try:
        # Login to GitHub
        if scraper.login_to_github():
            # Access Copilot Chat
            if scraper.access_copilot_chat():
                # Send a test message
                response = scraper.send_message("Write a Python function to calculate Fibonacci sequence")

                if response:
                    logger.info("Message sent and response received successfully")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    finally:
        # Always close the browser
        scraper.close()


if __name__ == '__main__':
    main()
