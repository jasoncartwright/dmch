#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Mail Comment Headlines (dmch)
Fetches the Daily Mail homepage and replaces headlines with top comments.
"""

import logging
import re
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup, NavigableString

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0'

def fetch_url(url, headers=None, timeout=30):
    """Fetch a URL and return the content."""
    if headers is None:
        headers = {'User-Agent': USER_AGENT}
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout) as response:
            return response.read(), response.status
    except (URLError, HTTPError) as e:
        logging.error(f"Error fetching {url}: {e}")
        return None, None


def main():
    """Main function to crawl Daily Mail and generate index.html"""
    
    dm_hp_url = "https://www.dailymail.co.uk/home/index.html"
    dm_comment_url = "https://secured.dailymail.co.uk/reader-comments/p/asset/readcomments/%s?max=1&sort=voteRating&order=desc&rcCache=shout"
    article_id_regex = r"article-(\d+)"
    
    # Fetch the Daily Mail homepage
    logging.info(f"Fetching Daily Mail homepage: {dm_hp_url}")
    dm_hp_content, status_code = fetch_url(dm_hp_url)
    
    if status_code != 200 or dm_hp_content is None:
        logging.error(f"Failed to fetch homepage. Status: {status_code}")
        sys.exit(1)
    
    logging.info(f"Got DM homepage {len(dm_hp_content)} bytes")
    
    # Parse the homepage
    dm_hp_content_soup = BeautifulSoup(dm_hp_content, 'html.parser')
    
    # Find all article links by href pattern, not just those with itemprop="url"
    article_re = re.compile(article_id_regex)
    article_href_pattern = re.compile(r'/[^/]+/article-\d+/')
    all_links = dm_hp_content_soup.find_all("a", href=article_href_pattern)
    
    # Group links by article ID
    articles_dict = {}
    for link in all_links:
        if "href" not in link.attrs:
            continue
        matches = article_re.findall(link["href"])
        if not matches:
            continue
        article_id = matches[0]
        if article_id not in articles_dict:
            articles_dict[article_id] = []
        articles_dict[article_id].append(link)
    
    logging.info(f"Found {len(articles_dict)} unique articles")
    
    # Process each article
    for i, (article_id, links) in enumerate(articles_dict.items()):
        headline_comment_url = dm_comment_url % article_id
        
        # Fetch top comment
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        comment_content, comment_status = fetch_url(headline_comment_url, headers=headers)
        
        if comment_status == 200 and comment_content:
            try:
                comment_data = json.loads(comment_content)
                # Safely access nested JSON structure
                if (comment_data.get("payload") and 
                    comment_data["payload"].get("page") and 
                    len(comment_data["payload"]["page"]) > 0):
                    comment = comment_data["payload"]["page"][0]["message"]
                    # Replace text for ALL links to this article
                    for link in links:
                        link.clear()
                        link.append(NavigableString(comment))
                        # Ensure full URL
                        if not link["href"].startswith("http"):
                            link["href"] = f"https://www.dailymail.co.uk{link['href']}"
                    logging.info(f"Processed article {i+1}/{len(articles_dict)}: {article_id} ({len(links)} links)")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                logging.debug(f"No comment found for article {article_id}: {e}")
        else:
            logging.debug(f"Failed to fetch comment for article {article_id}")
    
    # Convert back to string and fix URLs
    hp_str = str(dm_hp_content_soup)
    hp_str = hp_str.replace("http://scripts.dailymail.co.uk", "https://scripts.dailymail.co.uk")
    hp_str = hp_str.replace("http://i.dailymail.co.uk", "https://i.dailymail.co.uk")
    
    # Write to index.html
    output_file = "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(hp_str)
    
    logging.info(f"Successfully wrote output to {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
