#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script to verify that images in links are preserved during processing.
"""

import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import re

# Constants
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0'
MAX_MISSING_IDS_TO_DISPLAY = 10  # Maximum number of missing article IDs to display

def main():
    """Validate that images are preserved in the processed HTML"""
    
    print("="*70)
    print("IMAGE PRESERVATION VALIDATION")
    print("="*70)
    
    # Fetch original page
    print("\n1. Fetching original Daily Mail homepage...")
    dm_hp_url = 'https://www.dailymail.co.uk/home/index.html'
    headers = {'User-Agent': USER_AGENT}
    req = Request(dm_hp_url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            original_content = response.read()
        print("   ✓ Original page fetched successfully")
    except (URLError, HTTPError) as e:
        print(f"   ✗ Failed to fetch original page: {e}")
        return 1
    
    # Load processed page
    print("\n2. Loading processed index.html...")
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            processed_content = f.read()
        print("   ✓ Processed page loaded successfully")
    except (FileNotFoundError, IOError) as e:
        print(f"   ✗ Failed to load processed page: {e}")
        return 1
    
    # Parse both pages
    original_soup = BeautifulSoup(original_content, 'html.parser')
    processed_soup = BeautifulSoup(processed_content, 'html.parser')
    
    # Find article links
    article_href_pattern = re.compile(r'/[^/]+/article-\d+/')
    article_id_regex = r'article-(\d+)'
    
    print("\n3. Analyzing article links...")
    original_links = original_soup.find_all('a', href=article_href_pattern)
    processed_links = processed_soup.find_all('a', href=article_href_pattern)
    
    print(f"   Original page:  {len(original_links)} total article links")
    print(f"   Processed page: {len(processed_links)} total article links")
    
    # Count links with images
    print("\n4. Counting links with images...")
    original_img_links = [l for l in original_links if l.find('img') is not None]
    processed_img_links = [l for l in processed_links if l.find('img') is not None]
    
    print(f"   Original page:  {len(original_img_links)} links with images")
    print(f"   Processed page: {len(processed_img_links)} links with images")
    
    # Extract article IDs with images
    print("\n5. Comparing article IDs with image links...")
    def get_article_ids(links):
        ids = set()
        for link in links:
            matches = re.findall(article_id_regex, link.get('href', ''))
            if matches:
                ids.add(matches[0])
        return ids
    
    original_ids = get_article_ids(original_img_links)
    processed_ids = get_article_ids(processed_img_links)
    
    print(f"   Original page:  {len(original_ids)} unique articles with images")
    print(f"   Processed page: {len(processed_ids)} unique articles with images")
    
    missing_ids = original_ids - processed_ids
    if missing_ids:
        print(f"\n   ✗ WARNING: {len(missing_ids)} articles lost their images!")
        print(f"   Missing article IDs: {sorted(missing_ids)[:MAX_MISSING_IDS_TO_DISPLAY]}")
        return 1
    else:
        print(f"   ✓ All articles with images preserved!")
    
    extra_ids = processed_ids - original_ids
    if extra_ids:
        print(f"   ℹ Note: {len(extra_ids)} additional articles now have images")
    
    # Validate image preservation (optimized: search article links first, then check for images)
    print("\n6. Validating image elements...")
    original_article_links = original_soup.find_all('a', href=article_href_pattern)
    processed_article_links = processed_soup.find_all('a', href=article_href_pattern)
    
    original_imgs = sum(1 for link in original_article_links if link.find('img') is not None)
    processed_imgs = sum(1 for link in processed_article_links if link.find('img') is not None)
    
    print(f"   Original page:  {original_imgs} <img> tags in article links")
    print(f"   Processed page: {processed_imgs} <img> tags in article links")
    
    img_diff = processed_imgs - original_imgs
    if img_diff < 0:
        print(f"   ✗ WARNING: {abs(img_diff)} images were removed!")
        return 1
    elif img_diff > 0:
        print(f"   ℹ Note: {img_diff} additional images in processed page")
    else:
        print(f"   ✓ Image count matches exactly!")
    
    # Final summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"✓ Images in article links are correctly preserved")
    print(f"✓ {len(processed_img_links)} links with images found in processed page")
    print(f"✓ {processed_imgs} image elements found in article links")
    print(f"✓ All {len(processed_ids)} articles with images intact")
    print("\n" + "="*70)
    print("RESULT: ✓ VALIDATION PASSED")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
