import requests
import json
import re
import os
from bs4 import BeautifulSoup
import time
import random
# Removing the global import
# import psycopg2
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration - store in Lambda environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME', 'events_db')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT', '5432')

def get_db_connection():
    """Create and return a database connection"""
    # Import psycopg2 inside the function
    import psycopg2
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise e

def save_events_to_db(events):
    """Save events to the PostgreSQL database"""
    if not events:
        logger.info("No events to save to database.")
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    saved_count = 0
    
    try:
        for event in events:
            # Extract venue name from the primary_venue object
            venue_name = event.get('primary_venue', {}).get('name', '')
            
            # Convert postal_code to integer or NULL if not a valid integer
            postal_code_str = event.get('postal_code', '')
            try:
                postal_code = int(postal_code_str) if postal_code_str.strip() else None
            except (ValueError, AttributeError):
                postal_code = None
            
            # Insert the event - modified to match your actual schema
            cursor.execute("""
                INSERT INTO events (
                    eid, name, summary, start_date,
                    is_online_event, venue_name, postal_code
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (eid) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    summary = EXCLUDED.summary,
                    start_date = EXCLUDED.start_date,
                    is_online_event = EXCLUDED.is_online_event,
                    venue_name = EXCLUDED.venue_name,
                    postal_code = EXCLUDED.postal_code
            """, (
                event.get('eid', ''),
                event.get('name', ''),
                event.get('summary', ''),
                event.get('start_date', ''),
                event.get('is_online_event', False),
                venue_name,
                postal_code  # Now using the converted integer value
            ))
            saved_count += 1
            
        # Commit the transaction
        conn.commit()
        logger.info(f"Successfully saved {saved_count} events to database")
        return saved_count
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving to database: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def get_eventbrite_data(location_code=66213, max_pages=5):
    """Modified Eventbrite scraper function for Lambda environment"""
    location_slug = location_code
    
    # Headers to simulate a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    all_events = []  # Store all events across all pages
    
    # Process multiple pages - limit to fewer pages in Lambda for execution time constraints
    for page_num in range(1, max_pages + 1):
        # User-facing URL with page number
        page_url = f"https://www.eventbrite.com/d/{location_slug}/events--today/?page={page_num}"
        logger.info(f"Scraping page {page_num}/{max_pages}: {page_url}")
        
        try:
            # Get the page
            page_response = requests.get(page_url, headers=headers)
            page_response.raise_for_status()
            logger.info(f"Response status code: {page_response.status_code}")
            
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(page_response.text, 'html.parser')
            
            # Extract events from this page
            page_events = []
                
            # Extract from JSON-LD data
            logger.info(f"Looking for JSON-LD data on page {page_num}...")
            json_ld_tags = soup.find_all('script', type='application/ld+json')
            
            if json_ld_tags:
                logger.info(f"Found {len(json_ld_tags)} JSON-LD script tags")
                
                for script_idx, script in enumerate(json_ld_tags):
                    try:
                        json_data = json.loads(script.string)
                        
                        # Check if this is the script with itemListElement (events)
                        if isinstance(json_data, dict) and 'itemListElement' in json_data:
                            event_items = json_data['itemListElement']
                            logger.info(f"Found {len(event_items)} events in JSON-LD script #{script_idx+1}")
                            
                            events_from_jsonld = []
                            for event in event_items:
                                if 'item' in event:
                                    event_info = event['item']
                                    
                                    # Extract location details
                                    location = event_info.get('location', {})
                                    
                                    # Get address details
                                    address = location.get('address', {}) if isinstance(location, dict) else {}
                                    postal_code = address.get('postalCode', '') if isinstance(address, dict) else ''
                                    
                                    # Try to extract IDs from URLs
                                    url = event_info.get('url', '')
                                    eid = ''
                                    
                                    eid_match = re.search(r'tickets-(\d+)$', url) or re.search(r'tickets-(\d+)(?:[/?#]|$)', url) or re.search(r'/e/([^/?]+)', url)
                                    if eid_match:
                                        eid = eid_match.group(1)
                                    
                                    # Map data to our desired structure
                                    event_data = {
                                        'name': event_info.get('name', ''),
                                        'eid': eid,
                                        'summary': event_info.get('description', '')[:200] if event_info.get('description') else '',
                                        'start_date': event_info.get('startDate', ''),
                                        'end_date': event_info.get('endDate', ''),
                                        'is_online_event': event_info.get('eventAttendanceMode', '') == 'OnlineEventAttendanceMode' or 
                                                    (isinstance(location, dict) and location.get('@type') == 'VirtualLocation'),
                                        'primary_venue': {
                                            'name': location.get('name', '') if isinstance(location, dict) else ''
                                        },
                                        'postal_code': postal_code
                                    }
                                    events_from_jsonld.append(event_data)
                            
                            page_events.extend(events_from_jsonld)
                            
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing JSON-LD script #{script_idx+1}")
            else:
                logger.info(f"No JSON-LD data found on page {page_num}")
            
            # Check if we found any events on this page
            if not page_events:
                logger.info(f"No events found on page {page_num}. Stopping pagination.")
                break
            
            # Add this page's events to our total collection
            all_events.extend(page_events)
            
            logger.info(f"Added {len(page_events)} events from page {page_num}. Total events so far: {len(all_events)}")
            
            # Add a small delay between page requests to avoid rate limiting
            if page_num < max_pages:
                time.sleep(1.5)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on page {page_num}: {e}")
            break
        except Exception as e:
            logger.error(f"Error on page {page_num}: {e}")
            break
    
    logger.info(f"Total events extracted across all pages: {len(all_events)}")
    return all_events

# def lambda_handler(event, context):
#     """AWS Lambda entry point function"""
#     try:
#         # Default location code (can be overridden by event input)
#         location_code = event.get('location_code', 66213)
#         max_pages = event.get('max_pages', 5)  # Limit pages for Lambda execution time
        
#         logger.info(f"Starting Eventbrite data extraction for location code: {location_code}")
        
#         # Scrape Eventbrite events
#         events = get_eventbrite_data(location_code=location_code, max_pages=max_pages)
        
#         if not events:
#             return {
#                 'statusCode': 200,
#                 'body': json.dumps({
#                     'message': 'No events found',
#                     'count': 0,
#                     'location_code': location_code
#                 })
#             }
        
#         # Save events to database
#         saved_count = save_events_to_db(events)
        
#         return {
#             'statusCode': 200,
#             'body': json.dumps({
#                 'message': 'Success',
#                 'events_found': len(events),
#                 'events_saved': saved_count,
#                 'location_code': location_code
#             })
#         }
        
#     except Exception as e:
#         logger.error(f"Lambda execution error: {e}")
#         return {
#             'statusCode': 500,
#             'body': json.dumps({
#                 'message': f'Error: {str(e)}',
#                 'error_type': type(e).__name__
#             })
#         }

# def lambda_handler(event, context):
#     """AWS Lambda entry point function for testing without DB"""
#     try:
#         # Default location code (can be overridden by event input)
#         location_code = event.get('location_code', 66213)
#         max_pages = event.get('max_pages', 3)
        
#         logger.info(f"Starting Eventbrite data extraction for location code: {location_code}")
        
#         # Scrape Eventbrite events
#         events = get_eventbrite_data(location_code=location_code, max_pages=max_pages)
        
#         # Return sample of events without saving to database
#         sample_events = events[:5] if events else []
        
#         return {
#             'statusCode': 200,
#             'body': json.dumps({
#                 'message': 'Success',
#                 'events_found': len(events),
#                 'sample_events': sample_events
#             })
#         }
        
#     except Exception as e:
#         logger.error(f"Lambda execution error: {e}")
#         return {
#             'statusCode': 500,
#             'body': json.dumps({
#                 'message': f'Error: {str(e)}',
#                 'error_type': type(e).__name__
#             })
#         }




def lambda_handler(event, context):
    """AWS Lambda entry point function"""
    try:
        # Default location code (can be overridden by event input)
        location_code = event.get('location_code', 66213)
        max_pages = event.get('max_pages', 5)
        skip_db = event.get('skip_db', False)  # Optional flag to skip database operations
        
        logger.info(f"Starting Eventbrite data extraction for location code: {location_code}")
        
        # Scrape Eventbrite events
        events = get_eventbrite_data(location_code=location_code, max_pages=max_pages)
        
        if not events:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No events found',
                    'count': 0,
                    'location_code': location_code
                })
            }
        
        # Initialize saved_count here to avoid UnboundLocalError
        saved_count = 0
        
        # Save events to database if not skipped
        if not skip_db:
            try:
                saved_count = save_events_to_db(events)
                db_message = f"Successfully saved {saved_count} events to database"
            except Exception as db_error:
                logger.error(f"Database operation failed: {str(db_error)}")
                db_message = f"Database error: {str(db_error)}"
                # saved_count is already initialized to 0
        else:
            db_message = "Database operations skipped"
            # saved_count is already initialized to 0
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success',
                'events_found': len(events),
                'db_operation': db_message,
                'events_saved': saved_count if not skip_db else 'skipped',
                'location_code': location_code,
                'sample_events': events[:3] if events else []
            }, default=str)  # default=str handles date serialization
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}',
                'error_type': type(e).__name__
            })
        }