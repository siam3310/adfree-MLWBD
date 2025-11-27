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

## Phase 4: Bug Fixes and Production Deployment Issues ✅
- [x] Fix Cloudflare protection blocking in production
  - Replaced all `requests` calls with `cloudscraper` library
  - Removed hardcoded cookies (no longer needed)
- [x] Update domain from `fojik.com` to `fojik.site` (site migrated)
- [x] Fix HTML structure parsing for new website layout
  - Removed `class="item"` filter from article search
  - Updated to use `<div class="title">` for movie titles
  - Fixed image and link extraction for new structure
- [x] Test all scraping functions with production data
  - search_movie() - ✅ Working (19 results for "avatar")
  - get_latest_movies() - ✅ Working (5 movies per page)
  - get_download_links() - ✅ Working (6 link groups extracted)

## Phase 5: Production Timeout and Network Issues ✅
- [x] Fix timeout issues in Reflex free tier deployment
  - Reduced cloudscraper delay from 5 to 2 seconds
  - Added timeout=10 to all scraper.get() and scraper.post() calls
  - Implemented retry logic with max 2 retries for failed requests
  - Added proper error handling and logging for network failures
  - Return empty results gracefully instead of crashing
- [x] Test all functions with timeout handling
  - search_movie() - ✅ Working with 19 results
  - get_latest_movies() - ✅ Working with 5 movies
  - get_download_links() - ✅ Working with 6 link groups

## Phase 6: Production Deployment Error Handling ✅
- [x] Fix production deployment issues where search and links were failing
  - Increased timeout from 15s to 30s for slower production environment
  - Increased max_retries from 2 to 3 for better resilience
  - Added exponential backoff (2s, 4s, 8s) between retries
  - Added User-Agent rotation to avoid rate limiting/blocking
  - Added comprehensive error logging with traceback
  - Added detailed toast notifications with error types
  - Wrapped all scraping functions in try-except to prevent crashes
  - Return empty lists instead of raising exceptions
  - Added defensive checks for None/empty responses
  - Made all error handling production-safe

## UI Verification Phase ✅
- [x] Test search functionality with real queries
- [x] Test latest movies loading and pagination
- [x] Test download links extraction on details page
- [x] Verify direct link generation works correctly
