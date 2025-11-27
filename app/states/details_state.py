import reflex as rx
import logging
from typing import TypedDict
from app.mlwbd import get_download_links, get_main_link_


class DownloadLink(TypedDict):
    label: str
    url: str
    info: str


class DownloadGroup(TypedDict):
    title: str
    links: list[DownloadLink]


class DetailsState(rx.State):
    movie_url: str = ""
    download_groups: list[DownloadGroup] = []
    is_fetching_links: bool = False
    direct_link: str = ""
    selected_link_url: str = ""
    is_generating_direct: bool = False

    @rx.event
    def on_load(self):
        params = self.router.page.params
        url = params.get("url", "")
        self.download_groups = []
        self.direct_link = ""
        self.selected_link_url = ""
        self.is_generating_direct = False
        if url:
            self.movie_url = url
            return DetailsState.fetch_links
        else:
            self.movie_url = ""

    @rx.event
    def set_movie_url(self, url: str):
        self.movie_url = url

    @rx.event
    async def fetch_links(self):
        if not self.movie_url:
            yield rx.toast.warning("Please provide a Movie URL.")
            return
        self.is_fetching_links = True
        self.download_groups = []
        self.direct_link = ""
        yield
        try:
            logging.info(f"Fetching links for: {self.movie_url}")
            raw_links = get_download_links(self.movie_url)
            if not raw_links:
                logging.warning(f"No raw links returned for {self.movie_url}")
            normalized = []
            standalone_links = []
            for item in raw_links:
                if "links" in item and isinstance(item["links"], list):
                    group = {"title": item.get("title", "Download Links"), "links": []}
                    for link in item["links"]:
                        group["links"].append(
                            {
                                "label": link.get("label", "Link"),
                                "url": link.get("url", ""),
                                "info": link.get("type", ""),
                            }
                        )
                    if group["links"]:
                        normalized.append(group)
                elif "link" in item:
                    standalone_links.append(
                        {
                            "label": item.get("type", "Download"),
                            "url": item.get("link", ""),
                            "info": item.get("quality", ""),
                        }
                    )
                elif "url" in item:
                    standalone_links.append(
                        {
                            "label": item.get("label", "Download"),
                            "url": item.get("url", ""),
                            "info": item.get("type", ""),
                        }
                    )
            if standalone_links:
                normalized.append(
                    {"title": "Download Options", "links": standalone_links}
                )
            self.download_groups = normalized
            if not normalized:
                yield rx.toast.error(
                    "No links found. The site might be blocking our request or the structure changed.",
                    duration=5000,
                    close_button=True,
                )
        except Exception as e:
            error_type = type(e).__name__
            logging.exception(f"Error fetching links ({error_type}): {e}")
            yield rx.toast.error(
                f"Link extraction failed ({error_type}): {str(e)}",
                duration=6000,
                close_button=True,
            )
        finally:
            self.is_fetching_links = False

    @rx.event
    async def get_direct_link(self, url: str):
        self.selected_link_url = url
        self.is_generating_direct = True
        self.direct_link = ""
        yield
        try:
            result = get_main_link_(url)
            if result and result.startswith("http") and ("Error" not in result):
                self.direct_link = result
                yield rx.toast.success("Link generated successfully!")
            else:
                yield rx.toast.error(f"Failed: {result}")
        except Exception as e:
            logging.exception(f"Error generating link: {e}")
            yield rx.toast.error("An error occurred.")
        finally:
            self.is_generating_direct = False

    @rx.event
    def copy_to_clipboard(self):
        yield rx.set_clipboard(self.direct_link)
        yield rx.toast.success("Copied!")