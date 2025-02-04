import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re
from typing import Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://myanimelist.net"
        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def _get_page(self, url: str) -> BeautifulSoup:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            time.sleep(self.delay)
            return soup
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _get_anime_details(self, url: str) -> Dict[str, Any]:
        soup = self._get_page(url)
        if not soup:
            return None

        try:
            genres = [span.text for span in soup.select("span[itemprop='genre']")]
            synopsis = soup.find("p", {"itemprop": "description"})
            synopsis = synopsis.text.strip() if synopsis else ""
            studio = [
                link.text
                for link in soup.select("span:has(> a[href*='/anime/producer/'])")
            ]

            return {
                "genres": genres,
                "synopsis": synopsis,
                "studio": studio,
            }
        except Exception as e:
            logger.error(f"Error parsing anime details: {e}")
            return None

    def _get_manga_details(self, url: str) -> Dict[str, Any]:
        soup = self._get_page(url)
        if not soup:
            return None

        try:
            genres = [span.text for span in soup.select("span[itemprop='genre']")]
            synopsis = soup.find("p", {"itemprop": "description"})
            synopsis = synopsis.text.strip() if synopsis else ""
            authors = [link.text for link in soup.select("a[href*='/people/']")]

            return {
                "genres": genres,
                "synopsis": synopsis,
                "authors": authors,
            }
        except Exception as e:
            logger.error(f"Error parsing manga details: {e}")
            return None

    def _parse_anime_entry(self, entry) -> Dict[str, Any]:
        try:
            title_element = entry.find("h3", class_="fl-l fs14 fw-b anime_ranking_h3")
            title = title_element.text.strip() if title_element else "Unknown"
            url = title_element.find("a")["href"] if title_element else None

            info = entry.find("div", class_="information di-ib mt4")
            info_text = info.text.strip() if info else ""

            episodes_match = re.search(r"(\d+) eps?", info_text)
            episodes = int(episodes_match.group(1)) if episodes_match else None

            score_element = entry.find(
                "div", class_="js-top-ranking-score-col di-ib al"
            )
            score = float(score_element.text.strip()) if score_element else None

            members_element = entry.find(
                "div", class_="js-top-ranking-watching-num di-ib"
            )
            members = (
                int(members_element.text.strip().replace(",", ""))
                if members_element
                else None
            )

            details = self._get_anime_details(url) if url else {}

            return {
                "title": title,
                "episodes": episodes,
                "score": score,
                "members": members,
                "genres": details.get("genres", []) if details else [],
                "synopsis": details.get("synopsis", "") if details else "",
                "studio": details.get("studio", []) if details else [],
                "url": url,
                "media_type": "anime",
                "scrape_date": datetime.now().strftime("%Y-%m-%d"),
            }

        except Exception as e:
            logger.error(f"Error parsing anime entry: {e}")
            return None

    def _parse_manga_entry(self, entry) -> Dict[str, Any]:
        try:
            title_element = entry.find("h3", class_="manga_h3")
            title = title_element.text.strip() if title_element else "Unknown"
            url = title_element.find("a")["href"] if title_element else None

            info = entry.find("div", class_="information di-ib mt4")
            info_text = info.text.strip() if info else ""

            volumes_match = re.search(r"(\d+) vols?", info_text)
            volumes = int(volumes_match.group(1)) if volumes_match else None

            score_element = entry.find(
                "div", class_="js-top-ranking-score-col di-ib al"
            )
            score = float(score_element.text.strip()) if score_element else None

            members_element = entry.find(
                "div", class_="js-top-ranking-watching-num di-ib"
            )
            members = (
                int(members_element.text.strip().replace(",", ""))
                if members_element
                else None
            )

            details = self._get_manga_details(url) if url else {}

            return {
                "title": title,
                "volumes": volumes,
                "score": score,
                "members": members,
                "genres": details.get("genres", []) if details else [],
                "synopsis": details.get("synopsis", "") if details else "",
                "authors": details.get("authors", []) if details else [],
                "url": url,
                "media_type": "manga",
                "scrape_date": datetime.now().strftime("%Y-%m-%d"),
            }

        except Exception as e:
            logger.error(f"Error parsing manga entry: {e}")
            return None

    def scrape_top_anime(self, num_pages: int = 4) -> pd.DataFrame:
        all_anime = []
        for page in range(1, num_pages + 1):
            logger.info(f"Scraping anime page {page}")
            soup = self._get_page(
                f"{self.base_url}/topanime.php?limit={50 * (page - 1)}"
            )

            if not soup:
                continue

            anime_entries = soup.find_all("tr", class_="ranking-list")
            for entry in anime_entries:
                anime_data = self._parse_anime_entry(entry)
                if anime_data:
                    all_anime.append(anime_data)

        return pd.DataFrame(all_anime)

    def scrape_top_manga(self, num_pages: int = 4) -> pd.DataFrame:
        all_manga = []
        for page in range(1, num_pages + 1):
            logger.info(f"Scraping manga page {page}")
            soup = self._get_page(
                f"{self.base_url}/topmanga.php?limit={50 * (page - 1)}"
            )

            if not soup:
                continue

            manga_entries = soup.find_all("tr", class_="ranking-list")
            for entry in manga_entries:
                manga_data = self._parse_manga_entry(entry)
                if manga_data:
                    all_manga.append(manga_data)

        return pd.DataFrame(all_manga)
