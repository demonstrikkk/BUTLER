"""Base web automation class using Selenium."""
import time
import os
import platform
import subprocess
import shutil
from typing import Optional, List, Tuple
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config.settings import settings


class BaseAutomator:
    """Base class for web automation with common utilities."""
    
    def __init__(self, headless: bool = None):
        """Initialize the automator.
        
        Args:
            headless: Whether to run browser in headless mode (default: from settings)
        """
        self.headless = headless if headless is not None else settings.HEADLESS_MODE
        self.timeout = settings.BROWSER_TIMEOUT
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.screenshot_dir = settings.BASE_DIR / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def init_browser(self) -> None:
        """Initialize the Chrome browser - connect to existing Chrome or launch new."""
        if self.driver:
            return
        
        try:
            print("   🔧 Setting up Chrome browser...")
            
            chrome_options = Options()
            
            # Try to connect to existing Chrome instance first
            use_existing_chrome = settings.USE_EXISTING_CHROME if hasattr(settings, 'USE_EXISTING_CHROME') else True
            debugger_port = settings.CHROME_DEBUGGER_PORT if hasattr(settings, 'CHROME_DEBUGGER_PORT') else 9222
            
            if use_existing_chrome:
                try:
                    print(f"   🔗 Attempting to connect to existing Chrome on port {debugger_port}...")
                    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debugger_port}")
                    
                    print("   🔍 Installing/updating ChromeDriver...")
                    service = Service(ChromeDriverManager().install())
                    
                    print("   🚀 Connecting to your existing Chrome browser...")
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.wait = WebDriverWait(self.driver, self.timeout)
                    
                    print("   ✅ Connected to existing Chrome successfully!")
                    print("   📱 Using your logged-in session!")
                    return
                    
                except Exception as e:
                    print(f"   ⚠️ Could not connect to existing Chrome: {e}")
                    print("   💡 Attempting to launch Chrome with debugging enabled...")
                    
                    # Try to launch Chrome with debugging using subprocess
                    if self._launch_chrome_with_debugging(debugger_port):
                        # Try connecting again
                        try:
                            chrome_options = Options()  # Reset options
                            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debugger_port}")
                            
                            print("   🔗 Connecting to newly launched Chrome...")
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            self.wait = WebDriverWait(self.driver, self.timeout)
                            
                            print("   ✅ Connected to Chrome successfully!")
                            print("   📱 Using your logged-in session!")
                            return
                        except Exception as e2:
                            print(f"   ⚠️ Still could not connect: {e2}")
                    
                    print("   📖 See CHROME_PROFILE_GUIDE.md for manual setup instructions")
                    print("   🔄 Falling back to launching new Chrome with Selenium...")
            
            # Fallback: Launch new Chrome with profile
            use_profile = settings.USE_CHROME_PROFILE if hasattr(settings, 'USE_CHROME_PROFILE') else True
            
            if use_profile:
                user_data_dir = self._get_chrome_profile_path()
                
                if user_data_dir and os.path.exists(user_data_dir):
                    print(f"   👤 Using existing Chrome profile: {user_data_dir}")
                    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                    
                    # Use a specific profile (Default or Profile 1, etc.)
                    profile_name = settings.CHROME_PROFILE_NAME if hasattr(settings, 'CHROME_PROFILE_NAME') else "Default"
                    chrome_options.add_argument(f"--profile-directory={profile_name}")
                    print(f"   📂 Profile: {profile_name}")
                    print("   ✅ You'll be logged in to all your accounts!")
                else:
                    print(f"   ⚠️ Profile not found, using fresh browser")
            
            # Don't use headless mode when using profile (profile needs GUI)
            if self.headless and not use_profile:
                chrome_options.add_argument("--headless=new")
                print("   📱 Running in headless mode")
            elif use_profile or use_existing_chrome:
                print("   🖥️ Running in GUI mode (required for profile)")
            
            # Basic options that work across all Chrome versions
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # Only add experimental options if not connecting to existing Chrome
            # (these may not be compatible with all ChromeDriver versions)
            if not use_existing_chrome:
                try:
                    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    chrome_options.add_experimental_option('useAutomationExtension', False)
                except:
                    pass  # Ignore if these options are not supported
            
            # User agent to appear more natural
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            
            print("   🔍 Installing/updating ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            print("   🚀 Launching Chrome browser...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            # Execute CDP commands to mask automation
            try:
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    """
                })
            except:
                pass  # Some profiles may not allow CDP
            
            print("   ✅ Browser initialized successfully!")
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n   ❌ Failed to initialize browser: {error_msg}")
            
            if "chrome" in error_msg.lower():
                print("\n   💡 Chrome is not installed or not found!")
                print("      WSL/Linux: sudo apt-get install google-chrome-stable")
                print("      Or run this script on Windows (not in WSL)")
                print("      Or install Chrome from: https://www.google.com/chrome/")
            
            elif "driver" in error_msg.lower() or "executable" in error_msg.lower():
                print("\n   💡 ChromeDriver issue detected!")
                print("      The script should auto-download ChromeDriver...")
                print("      If it fails, manually download from:")
                print("      https://chromedriver.chromium.org/downloads")
            
            raise
    
    def _is_wsl(self) -> bool:
        """Detect if running in WSL (Windows Subsystem for Linux).
        
        Returns:
            True if running in WSL, False otherwise
        """
        try:
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                return 'microsoft' in content or 'wsl' in content
        except:
            return False
    
    def _get_chrome_executable_path(self) -> Optional[str]:
        """Get the Chrome executable path based on OS and environment.
        
        Returns:
            Path to Chrome executable or None
        """
        system = platform.system()
        
        if system == "Windows":
            # Windows paths
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        
        elif system == "Linux":
            if self._is_wsl():
                # WSL - use Windows Chrome executable
                possible_paths = [
                    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
                    "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        return path
            else:
                # Native Linux - check common locations
                chrome_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
                for cmd in chrome_commands:
                    chrome_path = shutil.which(cmd)
                    if chrome_path:
                        return chrome_path
        
        elif system == "Darwin":
            # macOS
            mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(mac_path):
                return mac_path
        
        return None
    
    def _launch_chrome_with_debugging(self, debugger_port: int = 9222) -> bool:
        """Launch Chrome with remote debugging enabled using subprocess.
        
        This works across Windows, Linux, macOS, and WSL by directly invoking
        the Chrome executable with the --remote-debugging-port flag.
        
        Args:
            debugger_port: Port to use for remote debugging (default: 9222)
            
        Returns:
            True if Chrome was launched successfully, False otherwise
        """
        try:
            chrome_path = self._get_chrome_executable_path()
            if not chrome_path:
                print("   ⚠️ Chrome executable not found")
                return False
            
            # Build command to launch Chrome
            cmd = [
                chrome_path,
                f"--remote-debugging-port={debugger_port}",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            
            # Add profile directory if specified
            profile_name = settings.CHROME_PROFILE_NAME if hasattr(settings, 'CHROME_PROFILE_NAME') else "Default"
            user_data_dir = self._get_chrome_profile_path()
            if user_data_dir and os.path.exists(user_data_dir):
                cmd.append(f"--user-data-dir={user_data_dir}")
                cmd.append(f"--profile-directory={profile_name}")
            
            print(f"   🚀 Launching Chrome with debugging on port {debugger_port}...")
            print(f"   📂 Chrome path: {chrome_path}")
            
            # Launch Chrome in background (detached process)
            if platform.system() == "Windows" or (platform.system() == "Linux" and self._is_wsl()):
                # Windows or WSL - use CREATE_NEW_PROCESS_GROUP to detach
                if platform.system() == "Windows":
                    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    # WSL - launch Windows executable from Linux
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Linux/macOS - use nohup-like behavior
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            
            print("   ⏳ Waiting for Chrome to start (5 seconds)...")
            time.sleep(5)  # Give Chrome time to start
            
            print("   ✅ Chrome launched successfully!")
            print(f"   🔗 Debug endpoint: http://localhost:{debugger_port}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to launch Chrome: {e}")
            return False
    
    def _get_chrome_profile_path(self) -> Optional[str]:
        """Get the Chrome user data directory path based on OS.
        
        Returns:
            Path to Chrome user data directory or None
        """
        system = platform.system()
        
        if system == "Windows":
            # Windows path
            username = os.environ.get('USERNAME', 'asus')
            return f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
        
        elif system == "Linux":
            # Check if running in WSL
            if self._is_wsl():
                # WSL - access Windows Chrome profile
                # Try to get Windows username from environment
                wsl_username = os.environ.get('USER', 'asus')
                # Check common Windows paths
                possible_users = [wsl_username]
                if os.path.exists("/mnt/c/Users"):
                    try:
                        users = os.listdir("/mnt/c/Users")
                        possible_users.extend([u for u in users if u not in ['Public', 'Default', 'Default User']])
                    except:
                        pass
                
                for username in possible_users:
                    wsl_path = f"/mnt/c/Users/{username}/AppData/Local/Google/Chrome/User Data"
                    if os.path.exists(wsl_path):
                        return wsl_path
            
            # Native Linux
            home = os.path.expanduser("~")
            linux_path = f"{home}/.config/google-chrome"
            if os.path.exists(linux_path):
                return linux_path
        
        elif system == "Darwin":
            # macOS
            home = os.path.expanduser("~")
            return f"{home}/Library/Application Support/Google/Chrome"
        
        return None
    
    def navigate_to(self, url: str) -> None:
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
        """
        if not self.driver:
            self.init_browser()
        self.driver.get(url)
        time.sleep(2)  # Allow page to load
    
    def find_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        parent: Optional[WebElement] = None
    ) -> Optional[WebElement]:
        """Find an element with wait.
        
        Args:
            by: By locator strategy (By.ID, By.XPATH, etc.)
            value: Locator value
            timeout: Custom timeout (default: use instance timeout)
            parent: Parent element to search within
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            wait_time = timeout or self.timeout
            if parent:
                return parent.find_element(by, value)
            else:
                return WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((by, value))
                )
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Element not found: {by}={value} - {e}")
            return None
    
    def find_elements(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> List[WebElement]:
        """Find multiple elements.
        
        Args:
            by: By locator strategy
            value: Locator value
            timeout: Custom timeout
            
        Returns:
            List of WebElements
        """
        try:
            wait_time = timeout or self.timeout
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return self.driver.find_elements(by, value)
        except (TimeoutException, NoSuchElementException):
            return []
    
    def click_element(self, element: WebElement, retry: int = 3) -> bool:
        """Click an element with retry logic.
        
        Args:
            element: Element to click
            retry: Number of retries
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(retry):
            try:
                # Wait for element to be clickable
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(element)
                )
                element.click()
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"Click attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        return False
    
    def type_text(self, element: WebElement, text: str, clear_first: bool = True) -> bool:
        """Type text into an element.
        
        Args:
            element: Element to type into
            text: Text to type
            clear_first: Whether to clear existing text first
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Typing failed: {e}")
            return False
    
    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> bool:
        """Wait for an element to appear.
        
        Args:
            by: By locator strategy
            value: Locator value
            timeout: Custom timeout
            
        Returns:
            True if element appears, False otherwise
        """
        try:
            wait_time = timeout or self.timeout
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def wait_and_click(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """Wait for element and click it.
        
        Args:
            by: By locator strategy
            value: Locator value
            timeout: Custom timeout
            
        Returns:
            True if successful, False otherwise
        """
        element = self.find_element(by, value, timeout)
        if element:
            return self.click_element(element)
        return False
    
    def scroll_to_element(self, element: WebElement) -> None:
        """Scroll an element into view.
        
        Args:
            element: Element to scroll to
        """
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
    
    def take_screenshot(self, name: str) -> Path:
        """Take a screenshot.
        
        Args:
            name: Screenshot name
            
        Returns:
            Path to the screenshot file
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        self.driver.save_screenshot(str(filepath))
        return filepath
    
    def get_text(self, by: By, value: str) -> Optional[str]:
        """Get text from an element.
        
        Args:
            by: By locator strategy
            value: Locator value
            
        Returns:
            Element text or None
        """
        element = self.find_element(by, value)
        return element.text if element else None
    
    def wait_for_page_load(self, timeout: int = 10) -> None:
        """Wait for page to finish loading.
        
        Args:
            timeout: Maximum wait time
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)
        except TimeoutException:
            print("Page load timeout")
    
    def close_browser(self) -> None:
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
    
    def __enter__(self):
        """Context manager entry."""
        self.init_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()
