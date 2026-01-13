"""Authentication module for handball.net"""

import requests
from typing import Optional
from pathlib import Path
from bs4 import BeautifulSoup


class HandballNetAuthenticator:
    """Handles authentication for handball.net"""
    
    def __init__(self, base_url: str, username: str, password: str, cert_path: Optional[str] = None, verify_ssl: bool = True):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.verify_ssl = verify_ssl
        self.cert_path = self._resolve_cert_path(cert_path) if cert_path else None
    
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
        Authenticate with handball.net
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            login_url = f"{self.base_url}/anmelden"
            
            # Debug: Show SSL settings
            verify = self.cert_path if self.cert_path else self.verify_ssl
            if self.cert_path:
                print(f"✓ Using certificate: {self.cert_path}")
            else:
                print(f"✓ SSL verification: {self.verify_ssl}")
            
            # Get login page to extract CSRF token or other required fields
            response = self.session.get(login_url, timeout=10, verify=verify)
            response.raise_for_status()
            
            # Parse form to find actual field names
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form')
            
            if form:
                # Extract all input fields from the form
                fields = {}
                for input_field in form.find_all('input'):
                    field_name = input_field.get('name')
                    field_value = input_field.get('value', '')
                    if field_name:
                        fields[field_name] = field_value
                
                print(f"✓ Found form fields: {list(fields.keys())}")
                
                # Update with credentials
                # Try common field names
                for username_field in ['username', 'email', 'login', 'benutzername', 'email_or_username']:
                    if username_field in fields:
                        fields[username_field] = self.username
                        break
                
                for password_field in ['password', 'passwd', 'pwd', 'passwort']:
                    if password_field in fields:
                        fields[password_field] = self.password
                        break
                
                print(f"✓ Prepared login data with fields: {[k for k in fields.keys() if k not in ['username', 'password']]}")
                login_data = fields
            else:
                print("⚠ No form found on login page")
                login_data = {
                    'username': self.username,
                    'password': self.password,
                }
            
            # Submit login form
            response = self.session.post(
                login_url,
                data=login_data,
                timeout=10,
                allow_redirects=True,
                verify=verify
            )
            response.raise_for_status()
            
            # Verify login success (check for user dashboard or similar)
            if 'logout' in response.text.lower() or 'abmelden' in response.text.lower():
                print("✓ Successfully authenticated with handball.net")
                return True
            else:
                print("✗ Authentication failed")
                print(f"  Response status: {response.status_code}")
                print(f"  Response contains 'logout': {'logout' in response.text.lower()}")
                print(f"  Response contains 'abmelden': {'abmelden' in response.text.lower()}")
                # Show first 500 chars of response to debug
                if len(response.text) > 0:
                    print(f"  Response preview: {response.text[:500]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Authentication error: {e}")
            return False
    
    def get_session(self) -> requests.Session:
        """Get authenticated session"""
        return self.session
    
    def logout(self) -> None:
        """Logout from handball.net"""
        self.session.close()
