import requests
import time
import json
import hashlib
from typing import Dict, List, Optional
from scrapy.http import Response
from scrapy import Request

from scrapper.spiders.base_spider import BaseSpider
from scrapper.items import FileItem, MetadataItem, Metadata, ScrappedItem
from api.models import EestiScrapperTask


class EestiSpider(BaseSpider):
    name = 'eesti_spider'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 0,  # Be respectful to eesti.ee
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if isinstance(kwargs.get('task'), EestiScrapperTask):
            self.task: EestiScrapperTask = kwargs.get('task')
        
        self.base_url = "https://www.eesti.ee"
        self.menu_api = f"{self.base_url}/api/menu/et"
        self.article_api = f"{self.base_url}/api/article/v2"
        self.start_urls = []  # We'll populate this from the API
        
        # Initialize with articles from API
        self.article_entries = self.fetch_all_article_entries()
        if self.article_entries:
            # Create start_urls from the first article to initialize Scrapy
            first_article = self.article_entries[0]
            self.start_urls = [f"{self.base_url}{first_article['href']}"]
    
    def fetch_menu(self) -> Optional[Dict]:
        """Fetch the menu structure from the API"""
        try:
            self.logger.info("Fetching Eesti.ee menu structure...")
            response = requests.get(self.menu_api, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching menu: {e}")
            return None
    
    def fetch_article(self, article_id: int) -> Optional[Dict]:
        """Fetch a specific article by ID"""
        try:
            url = f"{self.article_api}/{article_id}"
            self.logger.info(f"Fetching article {article_id}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching article {article_id}: {e}")
            return None
    
    def extract_article_ids(self, menu_data: Dict) -> List[Dict]:
        """Recursively extract all arvaArticleId values from the menu structure"""
        article_entries = []
        
        def recursive_search(item):
            if isinstance(item, dict):
                if 'arvaArticleId' in item:
                    entry = {
                        'id': item['arvaArticleId'],
                        'href': item.get('href', ''),
                        'title': item.get('title', ''),
                        'pageTitle': item.get('pageTitle', '')
                    }
                    article_entries.append(entry)
                
                for key, value in item.items():
                    if key == 'children' and isinstance(value, list):
                        for child in value:
                            recursive_search(child)
                    elif isinstance(value, (dict, list)):
                        recursive_search(value)
            
            elif isinstance(item, list):
                for sub_item in item:
                    recursive_search(sub_item)
        
        if 'data' in menu_data:
            recursive_search(menu_data['data'])
        else:
            recursive_search(menu_data)
        
        return article_entries
    
    def fetch_all_article_entries(self) -> List[Dict]:
        """Fetch all article entries from the menu API"""
        menu_data = self.fetch_menu()
        if not menu_data:
            self.logger.error("Failed to fetch menu data")
            return []
        
        article_entries = self.extract_article_ids(menu_data)
        self.logger.info(f"Found {len(article_entries)} articles to process")
        return article_entries

    async def start(self):
        """Override start method to process articles via API instead of web scraping"""
        if not self.article_entries:
            self.logger.error("No articles found to process")
            return
        
        for i, entry in enumerate(self.article_entries, 1):
            self.check_source_is_stopping()
            article_id = entry['id']
            href = entry['href']
            
            self.logger.info(f"Processing article {i}/{len(self.article_entries)}: ID {article_id}")
            
            # Fetch article data from API
            article_data = self.fetch_article(article_id)
            if article_data:
                # Create article URL
                article_url = f"{self.base_url}{href}" if href else f"{self.base_url}/article/{article_id}"
                
                # Process the article data
                yield self.create_scrapped_item(article_data, article_url, entry)
            else:
                self.logger.warning(f"Failed to fetch article {article_id}")
            
            # Add delay between requests
            if i < len(self.article_entries):
                time.sleep(self.custom_settings['DOWNLOAD_DELAY'])
    
    def create_scrapped_item(self, article_data: Dict, article_url: str, entry: Dict) -> ScrappedItem:
        """Create a ScrappedItem from API article data"""
        # Extract content and create HTML-like structure
        title = article_data.get('title', entry.get('title', ''))
        article_id = article_data.get('id', '')
        description = article_data.get('description', '')
        content = article_data.get('content', '')
        
        # Create full HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="{description}">
</head>
<body>
    <h1>{title}</h1>
    {content}
</body>
</html>"""
        
        # Convert to bytes
        body_bytes = html_content.encode('utf-8')
        
        # Calculate hash
        content_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()
        
        # Create file item
        file_item = FileItem(
            body=body_bytes,
            source_url=article_url,
            extension='.html'
        )
        
        # Create metadata item
        metadata_item = MetadataItem(
            file_type='.html',
            metadata=Metadata(),
            source_url=article_url,
            page_title=title,
            external_id=article_id
        )
        
        # Create scrapped item
        scrapped_item = ScrappedItem(
            file=file_item,
            metadata=metadata_item,
            hash=content_hash
        )
        
        return scrapped_item

    async def parse(self, response: Response, **kwargs):
        """Override parse - not used since we process via API"""
        # This method won't be called since we override start()
        pass
