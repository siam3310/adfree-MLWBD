import logging
from app.mlwbd import search_movie, get_download_links, get_main_link_


def test_scraper():
    print("1. Testing search_movie('avatar')...")
    movies = search_movie("avatar")
    print(f"Found {len(movies)} movies.")
    if not movies:
        print("No movies found. Skipping link extraction.")
        return
    first_movie = movies[0]
    print(f"First movie: {first_movie.get('title')} - {first_movie.get('link')}")
    if not first_movie.get("link"):
        print("No link in first movie result.")
        return
    print("""
2. Testing get_download_links()...""")
    links = get_download_links(first_movie["link"])
    print(f"Found {len(links)} link groups/items.")
    if not links:
        print("No download links found.")
        return
    target_url = None
    if isinstance(links[0], dict):
        if "links" in links[0]:
            if links[0]["links"]:
                target_url = links[0]["links"][0].get("url")
                print(f"Selected target URL from Strategy 1: {target_url}")
        elif "link" in links[0]:
            target_url = links[0].get("link")
            print(f"Selected target URL from Strategy 2: {target_url}")
    if target_url:
        print("""
3. Testing get_main_link_()...""")
        try:
            direct_link = get_main_link_(target_url)
            print(f"Direct Link Result: {direct_link}")
        except Exception as e:
            logging.exception(f"Direct link failed: {e}")
    else:
        print("Could not find a valid URL to test direct link generation.")


if __name__ == "__main__":
    test_scraper()