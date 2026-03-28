# Resilient Multi-Page Property Listings Scraper for NigeriaPropertyCentre
A web scraping tool to systematically collect property data (title, address, price, agent and their contact info, bedroom/bathroom/toilet/parking/SQM, and listing URL) across multiple pages and cities. Supports flexible search filters, error-resilient extraction, structured retry handling, and automated post-scrape data normalization using Pandas

![zachary-moneypenny-BCIgm0Qnfo8-unsplash](https://github.com/user-attachments/assets/e0c86087-c878-48f1-ab2a-545d5de70a3b)

Developed a robust Python-based web scraping pipeline to extract structured real estate data from NigeriaPropertyCentre.com. 

The scraper uses Playwright to interact with JavaScript-rendered listings and systematically navigates paginated results based on configurable search parameters such as listing type, city, and bedroom count. It extracts key property attributes including price, address, agent details, and property features (bedrooms, bathrooms, parking, and area).

## Key Features
- Resilient navigation with retry logic to handle intermittent failures
- Structured logging for traceability and debugging
- Safe retry logic with incremental backoff for page load failures
- Efficient error handling to maintain scraper 
- Flexible search filters: listing type, city, bedroom count
- Randomized delays to mimic human interaction and reduce detection risk
- Data normalization and transformation using pandas
- Privacy-aware handling of sensitive fields (agent contact masking)

The output is a clean, analysis-ready dataset, with a sample CSV export provided for safe sharing and downstream use.

This solution is tailored for efficient, reliable and repeatable extraction from NigeriaPropertyCentre, ensuring accuracy

## Tech Stack
    Language: Python 3.x
    Automation & Scraping: Playwright
    Data Processing & Cleaning: Pandas, Regex
    Resilience Handling: Incremental retry logic
    Output: Structured sample CSV and Logging system