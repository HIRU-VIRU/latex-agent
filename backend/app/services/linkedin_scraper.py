"""LinkedIn profile scraper for extracting certifications."""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import logging
import asyncio
import subprocess
import sys
import json
import tempfile
import os

logger = logging.getLogger(__name__)


def _run_playwright_script(profile_url: str) -> str:
    """Run Playwright in a separate process to avoid Windows asyncio issues."""
    # Create a temporary Python script that runs Playwright
    script = f'''
import sys
import io
from playwright.sync_api import sync_playwright
import time

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

profile_url = "{profile_url}"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--start-maximized']
    )
    context = browser.new_context(
        viewport={{'width': 1920, 'height': 1080}},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    page.goto(profile_url, timeout=60000, wait_until='domcontentloaded')
    
    # Check if redirected to login
    if 'login' in page.url or 'authwall' in page.url:
        # Wait for login - give user time to log in
        sys.stderr.write("Please log in to LinkedIn...\\n")
        page.wait_for_url(lambda url: 'login' not in url and 'authwall' not in url, timeout=120000)
        sys.stderr.write("Login successful!\\n")
        # Wait for page to fully load after login
        page.wait_for_load_state('networkidle', timeout=30000)
        page.wait_for_timeout(3000)
    else:
        # Already logged in, wait for page to load
        page.wait_for_load_state('networkidle', timeout=30000)
        page.wait_for_timeout(2000)
    
    # Scroll to load all content - use try/except to handle navigation
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(1000)
    except Exception as e:
        sys.stderr.write(f"Scroll error (ignored): {{e}}\\n")
        pass
    
    html = page.content()
    browser.close()
    print(html)
'''
    
    # Write script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script)
        script_path = f.name
    
    try:
        # Run the script in a separate process
        logger.info(f"Running Playwright script for: {profile_url}")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"Playwright script failed: {result.stderr}")
        
        return result.stdout
    finally:
        # Clean up temp file
        try:
            os.unlink(script_path)
        except:
            pass


async def scrape_linkedin_certifications(profile_url: str) -> List[Dict[str, str]]:
    """
    Scrape certifications from a LinkedIn profile URL.
    
    Args:
        profile_url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
    
    Returns:
        List of certification dictionaries with keys: name, issuer, date, credential_id, url
    """
    try:
        # Run Playwright in separate process to avoid Windows asyncio issues
        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(None, _run_playwright_script, profile_url)
        
        soup = BeautifulSoup(html, 'html.parser')
        certifications = []
        
        # Look for certification cards using LinkedIn's specific classes
        # LinkedIn uses: artdeco-card pv-profile-card break-words mt2
        cert_cards = soup.find_all('div', class_=lambda x: x and 'artdeco-card' in x and 'pv-profile-card' in x)
        
        logger.info(f"Found {len(cert_cards)} artdeco-card elements")
        
        for card in cert_cards:
            cert = {}
            
            # Extract certification name (usually in h3 or div with specific classes)
            name_elem = card.find(['h3', 'div'], class_=lambda x: x and ('pv-entity__summary-info-v2' in x or 't-16' in x or 't-bold' in x))
            if not name_elem:
                # Try finding any h3 in the card
                name_elem = card.find('h3')
            if name_elem:
                cert['name'] = name_elem.get_text(strip=True)
            
            # Extract issuer (usually in p or span tags)
            issuer_elem = card.find(['p', 'span'], class_=lambda x: x and ('pv-entity__secondary-title' in x or 't-14' in x or 't-normal' in x))
            if issuer_elem:
                cert['issuer'] = issuer_elem.get_text(strip=True)
            
            # Extract date
            date_elem = card.find(['time', 'span'], class_=lambda x: x and 'pv-entity__date' in x) if card else None
            if not date_elem:
                # Look for text containing "Issued"
                for span in card.find_all('span'):
                    text = span.get_text(strip=True)
                    if 'Issued' in text or 'issued' in text:
                        cert['date'] = text.replace('Issued', '').strip()
                        break
            else:
                cert['date'] = date_elem.get_text(strip=True)
            
            # Extract credential ID
            for elem in card.find_all(['span', 'div', 'p']):
                text = elem.get_text(strip=True)
                if 'Credential ID' in text:
                    # Try to get the next element or the text after "Credential ID:"
                    cred_text = text.replace('Credential ID:', '').replace('Credential ID', '').strip()
                    if cred_text:
                        cert['credential_id'] = cred_text
                    break
            
            # Extract URL (look for "See credential" link or any link in the card)
            url_elem = card.find('a', href=True)
            if url_elem and 'href' in url_elem.attrs:
                cert['url'] = url_elem['href']
            
            if cert.get('name'):  # Only add if we at least got a name
                certifications.append(cert)
                logger.info(f"Extracted certification: {cert.get('name')}")
        
        logger.info(f"Found {len(certifications)} certifications")
        return certifications
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error scraping LinkedIn profile: {str(e)}\n{error_details}")
        raise Exception(f"LinkedIn scraping failed: {str(e)}")


def parse_linkedin_url(url: str) -> Optional[str]:
    """
    Validate and normalize LinkedIn profile URL.
    
    Args:
        url: LinkedIn profile URL
    
    Returns:
        Normalized URL or None if invalid
    """
    if not url:
        return None
    
    # Remove trailing slashes
    url = url.rstrip('/')
    
    # Check if it's a valid LinkedIn profile URL
    if 'linkedin.com/in/' in url:
        return url
    
    # If it's just a username, construct full URL
    if not url.startswith('http'):
        return f"https://www.linkedin.com/in/{url}"
    
    return None
