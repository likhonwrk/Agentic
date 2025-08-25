"""
Selenium WebDriver wrapper for additional browser automation capabilities
"""

import logging
import os
from typing import Dict, List, Optional, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)


class SeleniumBrowserService:
    """Selenium-based browser automation service"""
    
    def __init__(self):
        self.drivers: Dict[str, webdriver.Remote] = {}
        self.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.timeout = int(os.getenv("BROWSER_TIMEOUT", "30"))
    
    def create_driver(self, browser: str = "chrome", driver_id: str = "default") -> str:
        """Create a new WebDriver instance"""
        try:
            if browser.lower() == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                
                driver = webdriver.Chrome(options=options)
                
            elif browser.lower() == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                
                driver = webdriver.Firefox(options=options)
                
            elif browser.lower() == "edge":
                options = EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                driver = webdriver.Edge(options=options)
                
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
            # Set timeouts
            driver.implicitly_wait(self.timeout)
            driver.set_page_load_timeout(self.timeout)
            
            self.drivers[driver_id] = driver
            logger.info(f"Created {browser} driver: {driver_id}")
            
            return driver_id
            
        except Exception as e:
            logger.error(f"Failed to create {browser} driver: {e}")
            raise
    
    def get_driver(self, driver_id: str = "default") -> webdriver.Remote:
        """Get a WebDriver instance"""
        driver = self.drivers.get(driver_id)
        if not driver:
            raise ValueError(f"Driver {driver_id} not found")
        return driver
    
    def navigate(self, url: str, driver_id: str = "default") -> Dict:
        """Navigate to a URL"""
        driver = self.get_driver(driver_id)
        driver.get(url)
        
        return {
            "url": driver.current_url,
            "title": driver.title
        }
    
    def find_element(self, selector: str, by: str = "css", driver_id: str = "default"):
        """Find an element"""
        driver = self.get_driver(driver_id)
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        
        by_type = by_mapping.get(by.lower(), By.CSS_SELECTOR)
        return driver.find_element(by_type, selector)
    
    def find_elements(self, selector: str, by: str = "css", driver_id: str = "default"):
        """Find multiple elements"""
        driver = self.get_driver(driver_id)
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        
        by_type = by_mapping.get(by.lower(), By.CSS_SELECTOR)
        return driver.find_elements(by_type, selector)
    
    def click_element(self, selector: str, by: str = "css", driver_id: str = "default") -> Dict:
        """Click an element"""
        element = self.find_element(selector, by, driver_id)
        element.click()
        
        return {"clicked": selector}
    
    def type_text(self, selector: str, text: str, by: str = "css", clear: bool = True, driver_id: str = "default") -> Dict:
        """Type text into an element"""
        element = self.find_element(selector, by, driver_id)
        
        if clear:
            element.clear()
        
        element.send_keys(text)
        
        return {"typed": text, "selector": selector}
    
    def get_text(self, selector: str, by: str = "css", driver_id: str = "default") -> str:
        """Get text from an element"""
        element = self.find_element(selector, by, driver_id)
        return element.text
    
    def get_attribute(self, selector: str, attribute: str, by: str = "css", driver_id: str = "default") -> str:
        """Get an attribute from an element"""
        element = self.find_element(selector, by, driver_id)
        return element.get_attribute(attribute)
    
    def wait_for_element(self, selector: str, by: str = "css", timeout: int = None, driver_id: str = "default"):
        """Wait for an element to be present"""
        driver = self.get_driver(driver_id)
        timeout = timeout or self.timeout
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        
        by_type = by_mapping.get(by.lower(), By.CSS_SELECTOR)
        wait = WebDriverWait(driver, timeout)
        
        return wait.until(EC.presence_of_element_located((by_type, selector)))
    
    def execute_script(self, script: str, driver_id: str = "default") -> Any:
        """Execute JavaScript"""
        driver = self.get_driver(driver_id)
        return driver.execute_script(script)
    
    def take_screenshot(self, filename: str = None, driver_id: str = "default") -> bytes:
        """Take a screenshot"""
        driver = self.get_driver(driver_id)
        
        if filename:
            driver.save_screenshot(filename)
            return None
        else:
            return driver.get_screenshot_as_png()
    
    def scroll_to_element(self, selector: str, by: str = "css", driver_id: str = "default"):
        """Scroll to an element"""
        driver = self.get_driver(driver_id)
        element = self.find_element(selector, by, driver_id)
        
        driver.execute_script("arguments[0].scrollIntoView();", element)
    
    def perform_action_chain(self, actions: List[Dict], driver_id: str = "default") -> Dict:
        """Perform a chain of actions"""
        driver = self.get_driver(driver_id)
        action_chain = ActionChains(driver)
        
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "move_to_element":
                element = self.find_element(action["selector"], action.get("by", "css"), driver_id)
                action_chain.move_to_element(element)
            elif action_type == "click":
                action_chain.click()
            elif action_type == "double_click":
                action_chain.double_click()
            elif action_type == "right_click":
                action_chain.context_click()
            elif action_type == "drag_and_drop":
                source = self.find_element(action["source"], action.get("by", "css"), driver_id)
                target = self.find_element(action["target"], action.get("by", "css"), driver_id)
                action_chain.drag_and_drop(source, target)
            elif action_type == "key_down":
                action_chain.key_down(action["key"])
            elif action_type == "key_up":
                action_chain.key_up(action["key"])
            elif action_type == "send_keys":
                action_chain.send_keys(action["keys"])
        
        action_chain.perform()
        
        return {"actions_performed": len(actions)}
    
    def close_driver(self, driver_id: str = "default"):
        """Close a WebDriver instance"""
        if driver_id in self.drivers:
            self.drivers[driver_id].quit()
            del self.drivers[driver_id]
            logger.info(f"Closed driver: {driver_id}")
    
    def cleanup(self):
        """Close all WebDriver instances"""
        for driver_id in list(self.drivers.keys()):
            self.close_driver(driver_id)
        
        logger.info("Selenium service cleanup complete")
