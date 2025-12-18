"""Test LinkedIn scraper with a sample profile URL."""
import asyncio
from app.services.linkedin_scraper import scrape_linkedin_certifications, parse_linkedin_url


async def test_scraper():
    # Test URL parsing
    test_urls = [
        "https://www.linkedin.com/in/satyanadella/",
        "satyanadella",
        "linkedin.com/in/satyanadella/",
    ]
    
    print("Testing URL parsing:")
    for url in test_urls:
        parsed = parse_linkedin_url(url)
        print(f"  {url} -> {parsed}")
    
    print("\nNote: LinkedIn scraping requires a public profile URL.")
    print("For testing, try with your own public LinkedIn profile URL:")
    print("Example: https://www.linkedin.com/in/your-username/")
    
    # You can test with a real URL here
    # test_url = "https://www.linkedin.com/in/your-username/"
    # certs = scrape_linkedin_certifications(test_url)
    # print(f"\nFound {len(certs)} certifications:")
    # for cert in certs:
    #     print(f"  - {cert.get('name', 'N/A')} by {cert.get('issuer', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
