"""
Browser Automation Service
Comprehensive browser automation using Playwright, Puppeteer, and CDP WebSocket
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

import websockets
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class BrowserTask:
    """Represents a browser automation task"""
    
    def __init__(self, task_id: str, action: str, **kwargs):
        self.task_id = task_id
        self.action = action
        self.params = kwargs
        self.status = "pending"
        self.result = None
        self.error = None


class CDPWebSocketClient:
    """Chrome DevTools Protocol WebSocket client"""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket = None
        self.message_id = 0
        self.pending_requests = {}
    
    async def connect(self):
        """Connect to CDP WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info(f"Connected to CDP WebSocket: {self.ws_url}")
        except Exception as e:
            logger.error(f"Failed to connect to CDP WebSocket: {e}")
            raise
    
    async def send_command(self, method: str, params: Dict = None) -> Dict:
        """Send a CDP command and wait for response"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        self.message_id += 1
        message = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        # Store pending request
        future = asyncio.Future()
        self.pending_requests[self.message_id] = future
        
        # Send message
        await self.websocket.send(json.dumps(message))
        
        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            del self.pending_requests[self.message_id]
            raise TimeoutError(f"CDP command {method} timed out")
    
    async def listen_for_responses(self):
        """Listen for CDP responses"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if "id" in data and data["id"] in self.pending_requests:
                    # Response to a command
                    future = self.pending_requests.pop(data["id"])
                    if "error" in data:
                        future.set_exception(Exception(data["error"]["message"]))
                    else:
                        future.set_result(data.get("result", {}))
                else:
                    # Event notification
                    logger.debug(f"CDP Event: {data.get('method', 'unknown')}")
        except Exception as e:
            logger.error(f"Error listening for CDP responses: {e}")
    
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()


class BrowserAutomationService:
    """Comprehensive browser automation service"""
    
    def __init__(self):
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.cdp_clients: Dict[str, CDPWebSocketClient] = {}
        self.active_tasks: Dict[str, BrowserTask] = {}
        
        # Configuration
        self.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    async def initialize(self):
        """Initialize browser automation service"""
        try:
            logger.info("Initializing Browser Automation Service...")
            
            # Initialize Playwright
            self.playwright = await async_playwright().start()
            
            # Launch default browsers
            await self._launch_default_browsers()
            
            logger.info("Browser Automation Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Browser Automation Service: {e}")
            raise
    
    async def _launch_default_browsers(self):
        """Launch default browser instances"""
        try:
            # Launch Chromium
            chromium = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--remote-debugging-port=9222"
                ]
            )
            self.browsers["chromium"] = chromium
            
            # Create default context
            context = await chromium.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.contexts["default"] = context
            
            logger.info("Default browsers launched successfully")
            
        except Exception as e:
            logger.error(f"Failed to launch default browsers: {e}")
            raise
    
    async def execute_task(
        self,
        action: str,
        url: Optional[str] = None,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        options: Dict = None
    ) -> Dict[str, Any]:
        """Execute a browser automation task"""
        
        task_id = str(uuid.uuid4())
        task = BrowserTask(
            task_id=task_id,
            action=action,
            url=url,
            selector=selector,
            text=text,
            options=options or {}
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Execute the task based on action type
            if action == "navigate":
                result = await self._navigate(url, options)
            elif action == "click":
                result = await self._click(selector, options)
            elif action == "type":
                result = await self._type(selector, text, options)
            elif action == "screenshot":
                result = await self._screenshot(options)
            elif action == "extract_text":
                result = await self._extract_text(selector, options)
            elif action == "extract_data":
                result = await self._extract_data(options)
            elif action == "wait_for_element":
                result = await self._wait_for_element(selector, options)
            elif action == "execute_script":
                result = await self._execute_script(text, options)
            elif action == "fill_form":
                result = await self._fill_form(options)
            elif action == "scroll":
                result = await self._scroll(options)
            elif action == "cdp_command":
                result = await self._execute_cdp_command(options)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            task.status = "completed"
            task.result = result
            
            return {
                "task_id": task_id,
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"Browser task {task_id} failed: {e}")
            
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
        finally:
            # Clean up completed task after some time
            asyncio.create_task(self._cleanup_task(task_id, delay=300))  # 5 minutes
    
    async def _get_page(self, context_name: str = "default") -> Page:
        """Get or create a page in the specified context"""
        context = self.contexts.get(context_name)
        if not context:
            raise ValueError(f"Context {context_name} not found")
        
        # Get existing page or create new one
        pages = context.pages
        if pages:
            return pages[0]
        else:
            return await context.new_page()
    
    async def _navigate(self, url: str, options: Dict) -> Dict:
        """Navigate to a URL"""
        page = await self._get_page(options.get("context", "default"))
        
        response = await page.goto(url, timeout=self.timeout)
        
        return {
            "url": page.url,
            "title": await page.title(),
            "status": response.status if response else None
        }
    
    async def _click(self, selector: str, options: Dict) -> Dict:
        """Click an element"""
        page = await self._get_page(options.get("context", "default"))
        
        await page.wait_for_selector(selector, timeout=self.timeout)
        await page.click(selector)
        
        return {"clicked": selector}
    
    async def _type(self, selector: str, text: str, options: Dict) -> Dict:
        """Type text into an element"""
        page = await self._get_page(options.get("context", "default"))
        
        await page.wait_for_selector(selector, timeout=self.timeout)
        
        if options.get("clear", True):
            await page.fill(selector, "")
        
        await page.type(selector, text, delay=options.get("delay", 50))
        
        return {"typed": text, "selector": selector}
    
    async def _screenshot(self, options: Dict) -> Dict:
        """Take a screenshot"""
        page = await self._get_page(options.get("context", "default"))
        
        screenshot_options = {
            "full_page": options.get("full_page", True),
            "type": options.get("format", "png")
        }
        
        if options.get("path"):
            screenshot_options["path"] = options["path"]
        
        screenshot_bytes = await page.screenshot(**screenshot_options)
        
        return {
            "screenshot": screenshot_bytes.hex() if not options.get("path") else None,
            "path": options.get("path"),
            "size": len(screenshot_bytes)
        }
    
    async def _extract_text(self, selector: str, options: Dict) -> Dict:
        """Extract text from elements"""
        page = await self._get_page(options.get("context", "default"))
        
        if selector:
            await page.wait_for_selector(selector, timeout=self.timeout)
            
            if options.get("all", False):
                elements = await page.query_selector_all(selector)
                texts = []
                for element in elements:
                    text = await element.text_content()
                    texts.append(text.strip() if text else "")
                return {"texts": texts, "count": len(texts)}
            else:
                element = await page.query_selector(selector)
                text = await element.text_content() if element else ""
                return {"text": text.strip() if text else ""}
        else:
            # Extract all text from page
            text = await page.text_content("body")
            return {"text": text.strip() if text else ""}
    
    async def _extract_data(self, options: Dict) -> Dict:
        """Extract structured data from page"""
        page = await self._get_page(options.get("context", "default"))
        
        extraction_script = options.get("script", """
        () => {
            // Default data extraction
            const data = {};
            
            // Extract title
            data.title = document.title;
            
            // Extract meta description
            const metaDesc = document.querySelector('meta[name="description"]');
            data.description = metaDesc ? metaDesc.content : '';
            
            // Extract headings
            data.headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
                tag: h.tagName.toLowerCase(),
                text: h.textContent.trim()
            }));
            
            // Extract links
            data.links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.textContent.trim(),
                href: a.href
            }));
            
            return data;
        }
        """)
        
        result = await page.evaluate(extraction_script)
        return {"data": result}
    
    async def _wait_for_element(self, selector: str, options: Dict) -> Dict:
        """Wait for an element to appear"""
        page = await self._get_page(options.get("context", "default"))
        
        state = options.get("state", "visible")  # visible, hidden, attached, detached
        timeout = options.get("timeout", self.timeout)
        
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        
        return {"selector": selector, "state": state}
    
    async def _execute_script(self, script: str, options: Dict) -> Dict:
        """Execute JavaScript on the page"""
        page = await self._get_page(options.get("context", "default"))
        
        result = await page.evaluate(script)
        
        return {"result": result}
    
    async def _fill_form(self, options: Dict) -> Dict:
        """Fill a form with data"""
        page = await self._get_page(options.get("context", "default"))
        
        form_data = options.get("data", {})
        results = {}
        
        for selector, value in form_data.items():
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, str(value))
                results[selector] = "success"
            except Exception as e:
                results[selector] = f"error: {str(e)}"
        
        # Submit form if requested
        if options.get("submit"):
            submit_selector = options.get("submit_selector", "input[type='submit'], button[type='submit']")
            try:
                await page.click(submit_selector)
                results["submit"] = "success"
            except Exception as e:
                results["submit"] = f"error: {str(e)}"
        
        return {"form_results": results}
    
    async def _scroll(self, options: Dict) -> Dict:
        """Scroll the page"""
        page = await self._get_page(options.get("context", "default"))
        
        direction = options.get("direction", "down")
        amount = options.get("amount", 500)
        
        if direction == "down":
            await page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            await page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == "top":
            await page.evaluate("window.scrollTo(0, 0)")
        elif direction == "bottom":
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        return {"scrolled": direction, "amount": amount}
    
    async def _execute_cdp_command(self, options: Dict) -> Dict:
        """Execute a Chrome DevTools Protocol command"""
        method = options.get("method")
        params = options.get("params", {})
        
        if not method:
            raise ValueError("CDP method is required")
        
        # Get CDP session from page
        page = await self._get_page(options.get("context", "default"))
        cdp_session = await page.context.new_cdp_session(page)
        
        result = await cdp_session.send(method, params)
        
        return {"cdp_result": result}
    
    async def create_context(self, context_name: str, options: Dict = None) -> str:
        """Create a new browser context"""
        browser = self.browsers.get("chromium")
        if not browser:
            raise RuntimeError("No browser available")
        
        context_options = options or {}
        context = await browser.new_context(**context_options)
        self.contexts[context_name] = context
        
        logger.info(f"Created browser context: {context_name}")
        return context_name
    
    async def close_context(self, context_name: str):
        """Close a browser context"""
        if context_name in self.contexts:
            await self.contexts[context_name].close()
            del self.contexts[context_name]
            logger.info(f"Closed browser context: {context_name}")
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get the status of a task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task_id,
            "action": task.action,
            "status": task.status,
            "result": task.result,
            "error": task.error
        }
    
    async def _cleanup_task(self, task_id: str, delay: int = 0):
        """Clean up a completed task after delay"""
        if delay > 0:
            await asyncio.sleep(delay)
        
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    async def cleanup(self):
        """Cleanup all browser resources"""
        try:
            # Close all contexts
            for context_name in list(self.contexts.keys()):
                await self.close_context(context_name)
            
            # Close all browsers
            for browser in self.browsers.values():
                await browser.close()
            
            # Stop Playwright
            if self.playwright:
                await self.playwright.stop()
            
            # Close CDP clients
            for cdp_client in self.cdp_clients.values():
                await cdp_client.close()
            
            logger.info("Browser Automation Service cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during browser automation cleanup: {e}")
