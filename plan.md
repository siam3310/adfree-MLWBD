# MLWBD Movie Scraper - Reflex Implementation Plan

## Overview
Build a complete movie search and download link extraction web application using Reflex, based on the Flask app from the GitHub repository. The app will allow users to search for movies, view results, and extract download links from MLWBD websites.

## Phase 1: Core Movie Search and Scraping Module ✅
- [x] Create mlwbd.py scraping module with BeautifulSoup
  - search_movie() function to search movies on MLWBD
  - get_download_links() function to extract download links from movie pages
  - get_main_link_() function to get direct download links
  - extract_all_links() helper function for parsing HTML structures
- [x] Install required dependencies (beautifulsoup4, requests, lxml)
- [x] Test scraping functions with real MLWBD URLs to verify functionality

## Phase 2: Main UI and Search Interface ✅
- [x] Create main State class with search functionality
  - search_query field for user input
  - search_results list to store movie results
  - is_loading boolean for search state
  - search_movie() event handler
- [x] Build home page UI with Material Design 3 principles
  - Header with app title and branding (red primary color)
  - Search input field with search icon
  - Search button with loading state
  - Results grid displaying movie cards with poster, title, year, quality
  - Empty state when no results
  - Error handling and toast notifications
- [x] Implement responsive grid layout for movie cards
- [x] Add hover effects and elevation changes on cards

## Phase 3: Movie Details and Download Links Extraction ✅
- [x] Create MovieDetailsState for individual movie pages
  - selected_movie_url field
  - download_links list
  - is_fetching_links boolean
  - get_download_links() event handler
  - get_direct_link() event handler for individual links
- [x] Build movie details page
  - Movie information display
  - "Get Download Links" button
  - Download links list with quality, size, type labels
  - "Get Direct Link" buttons for each download option
  - Copy to clipboard functionality
  - Manual URL input option
- [x] Implement navigation between search results and movie details
- [x] Add loading states and error handling for link extraction

## Phase 4: Bug Fixes and Latest Movies Feature
- [ ] Fix URL input field not updating when navigating to new movie details
  - Change from default_value to value for controlled input
  - Update on_load to properly reset state when navigating
- [ ] Add latest movies functionality to homepage
  - Create get_latest_movies() function in mlwbd.py to fetch homepage movies
  - Add pagination support with page parameter
  - Update SearchState with latest_movies, page, is_loading_more, has_more_movies
  - Add latest_movies display section on homepage with grid layout
  - Implement "Load More" button with loading states

## Final UI Verification Phase
- [ ] Test homepage with latest movies loading
- [ ] Test search functionality with real queries
- [ ] Test navigation from homepage movie cards to details page
- [ ] Verify URL input field updates correctly when clicking different movies
- [ ] Test download links extraction and direct link generation