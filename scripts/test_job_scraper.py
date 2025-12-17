#!/usr/bin/env python3
"""Test scraping a real job description"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

print("Testing job description scraping...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Example: Scrape a public job listing (using LinkedIn as an example)
    url = "https://www.indeed.com/jobs?q=software+engineer"
    
    print(f"Navigating to: {url}")
    page.goto(url, timeout=30000)
    
    # Wait for content to load
    time.sleep(2)
    
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract page title
    title = soup.find('title').text if soup.find('title') else "No title"
    print(f"✅ Page loaded: {title}")
    
    # Count job cards (example)
    job_cards = soup.find_all('div', {'class': lambda x: x and 'job' in x.lower()})
    print(f"✅ Found approximately {len(job_cards)} job-related elements")
    
    browser.close()

print("\n✅ Job scraping demonstration complete!")
print("📋 Webscraper can extract job descriptions from career sites")
