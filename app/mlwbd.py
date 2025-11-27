import cloudscraper
import re
import ast
import json
import logging
import time
import random
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]


def get_scraper():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}, delay=5
    )
    user_agent = random.choice(USER_AGENTS)
    scraper.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }
    )
    return scraper


def request_with_retry(scraper, method, url, max_retries=4, timeout=45, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            logging.info(f"Request attempt {attempt + 1}/{max_retries + 1} for {url}")
            if method.lower() == "post":
                response = scraper.post(url, timeout=timeout, **kwargs)
            else:
                response = scraper.get(url, timeout=timeout, **kwargs)
            if response.status_code != 200:
                logging.warning(f"Non-200 status code {response.status_code} for {url}")
            response.raise_for_status()
            return response
        except Timeout:
            logging.error(f"Timeout error on attempt {attempt + 1} for {url}")
            if attempt == max_retries:
                logging.exception(f"Max retries reached (Timeout) for {url}")
                return None
        except ConnectionError:
            logging.error(f"Connection error on attempt {attempt + 1} for {url}")
            if attempt == max_retries:
                logging.exception(f"Max retries reached (ConnectionError) for {url}")
                return None
        except HTTPError as e:
            logging.error(
                f"HTTP error {(e.response.status_code if e.response else 'unknown')} on attempt {attempt + 1} for {url}"
            )
            if attempt == max_retries:
                logging.exception(f"Max retries reached (HTTPError) for {url}")
                return None
        except Exception as e:
            logging.error(f"General error on attempt {attempt + 1} for {url}: {e}")
            if attempt == max_retries:
                logging.exception(f"Max retries reached (General) for {url}")
                return None
        sleep_time = 2 ** (attempt + 1)
        logging.info(f"Retrying in {sleep_time} seconds...")
        time.sleep(sleep_time)
    return None


def extract_all_links(soup):
    results = []
    for tag in soup.find_all(["h2", "p", "strong", "em", "span"]):
        text = tag.get_text(strip=True)
        if (
            any((keyword in text.lower() for keyword in ["epi", "batch", "part"]))
            or tag.name == "h2"
        ):
            title = text
            links = []
            next_sibling = tag.find_next_sibling()
            while next_sibling:
                if next_sibling.name in ["h2", "p"] and any(
                    (
                        kw in next_sibling.get_text().lower()
                        for kw in ["epi", "batch", "part"]
                    )
                ):
                    break
                if next_sibling.name == "ul":
                    for li in next_sibling.find_all("li"):
                        label_text = li.get_text(strip=True).split(":")
                        label = label_text[0] if label_text else "Unknown"
                        for a in li.find_all("a"):
                            href = a.get("href")
                            if not href:
                                continue
                            links.append(
                                {
                                    "label": label,
                                    "type": a.get_text(strip=True),
                                    "url": href,
                                }
                            )
                next_sibling = next_sibling.find_next_sibling()
            if links:
                results.append({"title": title, "links": links})
    if not results:
        fallback = []
        quality_blocks = soup.find_all("p", style=re.compile("text-align: center;"))
        for block in quality_blocks:
            text = block.get_text(separator=" ", strip=True)
            links = block.find_all("a")
            hrefs = [(a.text.strip(), a.get("href")) for a in links if a.get("href")]
            if hrefs and any((ext in text for ext in ["480p", "720p", "1080p"])):
                match = re.search(
                    "([\\d.]+(?:MB|GB).*?(480p|720p|1080p))", text, re.IGNORECASE
                )
                quality = match.group(1).strip() if match else "Unknown"
                for link_text, link_url in hrefs:
                    fallback.append(
                        {"quality": quality, "type": link_text, "link": link_url}
                    )
        return fallback
    return results


def search_movie(text):
    try:
        scraper = get_scraper()
        params = {"s": text}
        logging.info(f"Searching for movie: {text}")
        resp = request_with_retry(scraper, "get", "https://fojik.site/", params=params)
        if not resp:
            logging.error("No response received from search")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        movies_div = soup.find_all("article")
        logging.info(f"Found {len(movies_div)} article elements in search results")
        results = []
        for movie_div in movies_div:
            try:
                title_div = movie_div.find("div", class_="title")
                a_tag = (
                    title_div.find("a") if title_div else movie_div.find("a", href=True)
                )
                img_tag = movie_div.find("img", src=True)
                if a_tag:
                    title = a_tag.get_text(strip=True)
                elif img_tag and img_tag.get("alt"):
                    title = img_tag["alt"]
                else:
                    title = ""
                link = a_tag["href"] if a_tag else ""
                image = img_tag["src"] if img_tag else ""
                if title and link:
                    results.append({"title": title, "image": image, "link": link})
            except Exception as inner_e:
                logging.exception(
                    f"Skipping a movie element due to parse error: {inner_e}"
                )
                continue
        logging.info(f"Successfully parsed {len(results)} movies from search")
        return results
    except Exception as e:
        logging.exception(f"Error searching movie: {e}")
        return []


def get_latest_movies(page=1):
    scraper = get_scraper()
    url = f"https://fojik.site/page/{page}/"
    try:
        resp = request_with_retry(scraper, "get", url)
        soup = BeautifulSoup(resp.text, "html.parser")
        movies_div = soup.find_all("article")
        results = []
        for movie_div in movies_div:
            title_div = movie_div.find("div", class_="title")
            a_tag = title_div.find("a") if title_div else movie_div.find("a", href=True)
            img_tag = movie_div.find("img", src=True)
            if a_tag:
                title = a_tag.get_text(strip=True)
            elif img_tag and img_tag.get("alt"):
                title = img_tag["alt"].strip()
            else:
                title = ""
            link = a_tag["href"] if a_tag else ""
            image = img_tag["src"] if img_tag else ""
            if title and link:
                results.append({"title": title, "image": image, "link": link})
        return results
    except Exception as e:
        logging.exception(f"Error fetching latest movies: {e}")
        return []


def get_download_links(url):
    scraper = get_scraper()
    logging.info(f"Starting download link extraction for: {url}")
    try:
        response = request_with_retry(scraper, "get", url)
        if not response:
            logging.error(f"Failed to load initial URL: {url}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        fu_input = soup.find("input", {"type": "hidden", "name": "FU"})
        fn_input = soup.find("input", {"type": "hidden", "name": "FN"})
        if not fu_input or not fn_input:
            logging.error("Could not find FU or FN inputs on initial page")
            return []
        FU = fu_input["value"]
        FN = fn_input["value"]
        logging.info("Step 1: Found FU and FN inputs")
        response = request_with_retry(
            scraper,
            "post",
            "https://search.technews24.site/blog.php",
            data={"FU": FU, "FN": FN},
            headers={"Referer": url},
        )
        soup = BeautifulSoup(response.text, "html.parser")
        fu2_input = soup.find("input", {"type": "hidden", "name": "FU2"})
        if not fu2_input:
            logging.error(
                "Step 2 Failed: Could not find FU2 input in blog.php response"
            )
            return []
        FU2 = fu2_input["value"]
        logging.info("Step 2: Found FU2 input")
        response = request_with_retry(
            scraper,
            "post",
            "https://freethemesy.com/dld.php",
            data={"FU2": FU2},
            headers={"Referer": "https://search.technews24.site/"},
        )
        ss_match = re.search("var sss = '(.*?)'; var", response.text)
        fetch_match = re.search("_0x12fb2a=(.*?);_0x3073", response.text)
        if not fetch_match:
            logging.info("Specific regex failed, trying generic pattern for JS array")
            fetch_match = re.search(
                "var\\s+(_0x[a-f0-9]+)\\s*=\\s*(\\[.*?\\]);", response.text
            )
            if fetch_match:
                fetch_str_list = fetch_match.group(2)
            else:
                fetch_str_list = None
        else:
            fetch_str_list = fetch_match.group(1)
        if not ss_match or not fetch_str_list:
            logging.error(
                "Step 3 Failed: Could not find JS variables sss or array in dld.php response"
            )
            logging.debug(f"Response snippet: {response.text[:500]}")
            return []
        ss = ss_match.group(1)
        try:
            fetch_str_list = ast.literal_eval(fetch_str_list)
            v = fetch_str_list[18]
        except Exception as ast_err:
            logging.exception(f"Step 3 Failed: AST parsing error: {ast_err}")
            return []
        logging.info("Step 3: Extracted sss and v variables")
        final_url = "https://freethemesy.com/new/l/api/m"
        payload = {"s": ss, "v": v}
        headers = {
            "Referer": "https://freethemesy.com/dld.php",
            "Origin": "https://freethemesy.com",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        final_response_obj = request_with_retry(
            scraper, "post", final_url, data=payload, headers=headers
        )
        final_response_down_page = final_response_obj.text.strip()
        if not final_response_down_page.startswith("http"):
            logging.error(
                f"Step 4 Failed: API returned non-URL: {final_response_down_page[:100]}"
            )
            return []
        logging.info(
            f"Step 4: Received final download page URL: {final_response_down_page}"
        )
        response = request_with_retry(scraper, "get", final_response_down_page)
        soup = BeautifulSoup(response.text, "html.parser")
        links = extract_all_links(soup)
        logging.info(
            f"Step 5: Extracted {(len(links) if isinstance(links, list) else 0)} raw link groups"
        )
        if isinstance(links, list):
            filtered_links = []
            for item in links:
                if isinstance(item, dict) and "links" in item:
                    item["links"] = [
                        l for l in item["links"] if ".me" not in l.get("url", "")
                    ]
                    if item["links"]:
                        filtered_links.append(item)
                elif isinstance(item, dict) and "link" in item:
                    if ".me" not in item["link"]:
                        filtered_links.append(item)
                elif isinstance(item, dict) and "url" in item:
                    if ".me" not in item["url"]:
                        filtered_links.append(item)
            links = filtered_links
        logging.info(f"Final: Returning {len(links)} filtered link groups")
        return links
    except Exception as e:
        logging.exception(f"CRITICAL Error extracting download links: {e}")
        return []


def get_main_link_(url):
    scraper = get_scraper()
    try:
        response = request_with_retry(scraper, "get", url)
        soup = BeautifulSoup(response.text, "html.parser")
        fu5_input = soup.find("input", {"type": "hidden", "name": "FU5"})
        if not fu5_input:
            return "Error: FU5 not found"
        FU5 = fu5_input["value"]
        response = request_with_retry(
            scraper,
            "post",
            "https://sharelink-3.site/dld.php",
            data={"FU5": FU5},
            headers={"Referer": url},
        )
        soup = BeautifulSoup(response.text, "html.parser")
        fu7_input = soup.find("input", {"type": "hidden", "name": "FU7"})
        if not fu7_input:
            return "Error: FU7 not found"
        FU7 = fu7_input["value"]
        response = request_with_retry(
            scraper,
            "post",
            "https://sharelink-3.site/blog/",
            data={"FU7": FU7},
            headers={"Referer": "https://sharelink-3.site/dld.php"},
        )
        sss_match = re.search("var sss = '(.*?)';", response.text)
        v_match = re.search("v: '(.*?)'", response.text)
        if not sss_match or not v_match:
            return "Error: sss or v not found in JS"
        sss = sss_match.group(1)
        __v = v_match.group(1)
        url_api = "https://sharelink-3.site/l/api/m"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://sharelink-3.site/blog/",
        }
        payload = {"s": sss, "v": __v}
        response = request_with_retry(
            scraper, "post", url_api, headers=headers, json=payload
        )
        return response.text
    except Exception as e:
        logging.exception(f"Error getting main link: {e}")
        return f"Error getting main link: {str(e)}"