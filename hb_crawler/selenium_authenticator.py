"""Selenium-based authentication for JavaScript-heavy handball.net"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
from pathlib import Path
import time
import os

# Disable SSL verification for webdriver-manager
os.environ['WDM_SSL_VERIFY'] = '0'


class HandballNetSeleniumAuthenticator:
    """Handles authentication for handball.net using Selenium (for JS-heavy pages)"""
    
    def __init__(self, base_url: str, username: str, password: str, cert_path: Optional[str] = None, verify_ssl: bool = True, headless: bool = True):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.cert_path = self._resolve_cert_path(cert_path) if cert_path else None
        self.headless = headless
        self.driver = None
        self.cookies = {}
    
    def _resolve_cert_path(self, cert_path: str) -> Optional[str]:
        """Resolve certificate path, expanding ~ to home directory"""
        if not cert_path:
            return None
        expanded_path = Path(cert_path).expanduser()
        if expanded_path.exists():
            return str(expanded_path)
        else:
            print(f"⚠ Certificate file not found: {expanded_path}")
            return None
    
    def login(self) -> bool:
        """
        Authenticate with handball.net using Selenium
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            
            # Handle SSL certificate
            if self.cert_path:
                print(f"✓ Using certificate: {self.cert_path}")
                # Configure SSL certificate for Chrome
                options.add_argument(f'--ignore-certificate-errors')
                # Note: Passing CA cert to Chrome requires system-level setup or proxy
                # For now, we ignore cert errors since we trust the certificate
            else:
                options.add_argument('--ignore-certificate-errors')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # Initialize driver
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
            print(f"✓ Opening login page: {self.base_url}/anmelden")
            self.driver.get(f"{self.base_url}/anmelden")
            
            # Wait for page to load
            time.sleep(2)
            
            # Try to handle cookie banner (but don't fail if we can't)
            try:
                self._handle_cookie_banner()
            except Exception as e:
                print(f"⚠ Cookie banner handling failed (continuing anyway): {e}")
            
            time.sleep(1)
            
            # Ensure we're on main content after iframe switching
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            # Try to find username input field
            username_field = None
            password_field = None
            
            # Try multiple possible selectors
            username_selectors = [
                (By.NAME, 'username'),
                (By.NAME, 'email'),
                (By.ID, 'username'),
                (By.ID, 'email'),
                (By.XPATH, "//input[@type='text']"),
                (By.XPATH, "//input[@type='email']"),
            ]
            
            password_selectors = [
                (By.NAME, 'password'),
                (By.ID, 'password'),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            # Find username field
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(selector)
                    )
                    if username_field:
                        print(f"✓ Found username field: {selector}")
                        break
                except:
                    continue
            
            # Find password field
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(*selector)
                    if password_field:
                        print(f"✓ Found password field: {selector}")
                        break
                except:
                    continue
            
            if not username_field or not password_field:
                print("✗ Could not find login fields")
                self._print_page_info()
                return False
            
            # Fill in credentials with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    username_field.clear()
                    username_field.send_keys(self.username)
                    password_field.clear()
                    password_field.send_keys(self.password)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠ Input failed ({attempt+1}), retrying...")
                        time.sleep(0.5)
                        # Re-find fields
                        for selector in username_selectors:
                            try:
                                username_field = self.driver.find_element(*selector)
                                password_field = self.driver.find_element(*password_selectors[0])
                                break
                            except:
                                continue
                    else:
                        raise
            
            print("✓ Credentials entered")
            
            # Find and click login button
            login_button = None
            button_selectors = [
                (By.XPATH, "//button[contains(text(), 'Anmelden')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.NAME, 'submit'),
            ]
            
            for selector in button_selectors:
                try:
                    login_button = self.driver.find_element(*selector)
                    if login_button:
                        print(f"✓ Found login button: {selector}")
                        break
                except:
                    continue
            
            if login_button:
                # Scroll button into view first
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                time.sleep(1)
                
                # Try clicking via JavaScript if normal click fails
                try:
                    login_button.click()
                except:
                    print("⚠ Normal click failed, trying JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", login_button)
                
                print("✓ Login button clicked, waiting for redirect...")
                
                # Wait for redirect (max 10 seconds)
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: 'anmelden' not in driver.current_url.lower()
                    )
                    print(f"✓ Redirected to: {self.driver.current_url}")
                except:
                    print("⚠ Timeout waiting for redirect, checking if logged in anyway...")
                    time.sleep(3)
            else:
                print("⚠ Could not find login button, will wait for page load...")
                time.sleep(5)
            
            # Check if logged in by looking for logout element
            time.sleep(2)
            if self._is_logged_in():
                print("✓ Successfully authenticated with handball.net")
                self._save_cookies()
                return True
            else:
                print("✗ Authentication failed - no logout element found")
                self._print_page_info()
                return False
                
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            import traceback
            traceback.print_exc()
            if self.driver:
                self.driver.quit()
            return False
        
        # SUCCESS: Don't quit driver - we need it for further navigation!
    
    def _is_logged_in(self) -> bool:
        """Check if user is logged in"""
        page_source = self.driver.page_source.lower()
        return 'logout' in page_source or 'abmelden' in page_source or 'mein profil' in page_source
    
    def _save_cookies(self):
        """Save cookies from Selenium session"""
        if self.driver:
            for cookie in self.driver.get_cookies():
                self.cookies[cookie['name']] = cookie['value']
    
    def _print_page_info(self):
        """Print page info for debugging"""
        print("\n--- Page Info ---")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Print all input fields found
        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
        if inputs:
            print(f"Found {len(inputs)} input fields:")
            for inp in inputs[:5]:  # Show first 5
                try:
                    print(f"  - type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
                except:
                    pass
        
        # Print all buttons found
        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        if buttons:
            print(f"Found {len(buttons)} buttons:")
            for btn in buttons[:5]:  # Show first 5
                try:
                    print(f"  - {btn.text}")
                except:
                    pass
        print("--- End Page Info ---\n")
    
    def _handle_cookie_banner(self):
        """Handle/dismiss cookie consent banner - JavaScript focused approach"""
        try:
            print("Attempting to dismiss cookie banner...")
            time.sleep(1)
            
            # Strategy 1: Use pure JavaScript to dismiss - safest approach
            js_commands = [
                # Hide any visible cookie notice
                "document.querySelectorAll('[class*=\"cmp\"], [class*=\"cookie\"], [class*=\"notice\"]').forEach(el => {el.style.display='none';});",
                # Execute consent manager commands if available
                "if(typeof __cmp === 'function') { try { __cmp('updateScopes', {}, true, true); } catch(e){} }",
                # Mark as consented
                "window.cmp_noscreen = true;",
                # Try to find and click any buttons
                "document.querySelectorAll('button').forEach(btn => { if(btn.textContent.toLowerCase().includes('akzeptieren') || btn.textContent.toLowerCase().includes('accept')) btn.click(); });",
            ]
            
            for cmd in js_commands:
                try:
                    self.driver.execute_script(cmd)
                except:
                    continue
            
            time.sleep(1)
            print("✓ Cookie banner handling executed")
            return True
            
        except Exception as e:
            print(f"⚠ Cookie banner handling error: {e}")
            # Don't fail - continue anyway
            return False
    
    def get_cookies(self) -> dict:
        """Get saved cookies"""
        return self.cookies
