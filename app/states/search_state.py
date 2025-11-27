import reflex as rx
import logging
from app.mlwbd import search_movie, get_latest_movies


class SearchState(rx.State):
    search_query: str = ""
    search_results: list[dict[str, str]] = []
    is_loading: bool = False
    has_searched: bool = False
    latest_movies: list[dict[str, str]] = []
    page: int = 1
    is_loading_more: bool = False
    has_more_movies: bool = True
    is_initial_loading: bool = False

    @rx.event
    def on_load(self):
        if not self.latest_movies:
            return SearchState.load_latest_movies

    @rx.event
    async def load_latest_movies(self):
        self.is_initial_loading = True
        self.page = 1
        self.latest_movies = []
        self.has_more_movies = True
        yield
        try:
            movies = get_latest_movies(self.page)
            self.latest_movies = movies
            if not movies:
                self.has_more_movies = False
        except Exception as e:
            logging.exception(f"Error loading latest movies: {e}")
            yield rx.toast.error("Failed to load latest movies.")
        finally:
            self.is_initial_loading = False

    @rx.event
    async def load_more_movies(self):
        if self.is_loading_more or not self.has_more_movies:
            return
        self.is_loading_more = True
        yield
        try:
            self.page += 1
            new_movies = get_latest_movies(self.page)
            if new_movies:
                self.latest_movies = self.latest_movies + new_movies
            else:
                self.has_more_movies = False
        except Exception as e:
            logging.exception(f"Error loading more movies: {e}")
            self.page -= 1
            yield rx.toast.error("Failed to load more movies.")
        finally:
            self.is_loading_more = False

    @rx.event
    async def search_movie_event(self):
        query = self.search_query.strip()
        if not query:
            yield rx.toast.warning(
                "Please enter a search term", duration=3000, close_button=True
            )
            return
        if (
            query.startswith("http://") or query.startswith("https://")
        ) and "fojik.com" in query:
            yield rx.toast.info(
                "Direct link detected! Redirecting to details...",
                duration=3000,
                close_button=True,
            )
            yield rx.redirect(f"/details?url={query}")
            return
        self.is_loading = True
        self.has_searched = True
        self.search_results = []
        yield
        try:
            results = search_movie(query)
            self.search_results = results
            if not results:
                yield rx.toast.info(
                    "No results found for your query", duration=3000, close_button=True
                )
        except Exception as e:
            logging.exception(f"Search error: {e}")
            yield rx.toast.error(
                "An error occurred while searching. Please try again.",
                duration=5000,
                close_button=True,
            )
        finally:
            self.is_loading = False

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def handle_key_down(self, key: str):
        if key == "Enter":
            return SearchState.search_movie_event