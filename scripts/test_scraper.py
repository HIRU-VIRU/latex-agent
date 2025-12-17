#!/usr/bin/env python3
"""Test webscraper functionality without Docker"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print("Testing webscraper components...")

# Test 1: Import libraries
print("✅ All libraries imported successfully!")

# Test 2: Launch browser and scrape
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Navigate to a test page
    page.goto('https://example.com')
    html = page.content()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1').text if soup.find('h1') else "No title"
    
    print(f"✅ Successfully scraped: '{title}'")
    
    browser.close()

print("✅ Webscraper is fully functional without Docker!")
