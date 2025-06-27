from flask import Flask, request, jsonify, render_template, Response
from datetime import datetime
import logging
import os
import json
import traceback
import psycopg2
from psycopg2.extras import RealDictCursor
from main_sse import main as main_sse_function

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database connection function
def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    # Get database connection parameters from environment or use defaults
    db_host = os.environ.get('DB_HOST') or 'localhost'
    db_name = os.environ.get('DB_NAME') or 'events_db'
    db_user = os.environ.get('DB_USER') or 'postgres'
    db_password = os.environ.get('DB_PASSWORD') or 'postgres'
    db_port = os.environ.get('DB_PORT') or '5432'
    
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def save_user_data(data):
    """Save user data to the database with proper type handling"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Extract user data
        business_name = data.get('business_name')
        business_type = data.get('business_type')
        business_email = data.get('business_email')
        business_postal_code = data.get('business_postal_code')
        business_latitude = data.get('business_latitude')
        business_longitude = data.get('business_longitude')
        
        # Insert user data with upsert based on email
        if business_email:
            cursor.execute("""
                INSERT INTO user_data 
                    (name, type, email, postal_code, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    postal_code = EXCLUDED.postal_code,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    last_updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                business_name,
                business_type,
                business_email,
                business_postal_code,
                business_latitude,
                business_longitude
            ))
        else:
            # If no email, create a new record
            cursor.execute("""
                INSERT INTO user_data 
                    (name, type, postal_code, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                business_name,
                business_type,
                business_postal_code,
                business_latitude,
                business_longitude
            ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving user data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_registered_users():
    """Get all registered users who have email addresses from the database"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT id, name, type, email, postal_code, latitude, longitude
            FROM user_data
            WHERE email IS NOT NULL AND email != ''
        """)
        
        users = cursor.fetchall()
        return users
    except Exception as e:
        logger.error(f"Error fetching registered users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate advertising recommendations"""
    try:
        data = request.json
        logger.info(f"Received request: {data}")
        
        # Save the user data to the database
        user_id = save_user_data(data)
            
        # Call the main function from main_sse.py
        result = main_sse_function(data)
        
        # Add the user_id to the result
        if user_id:
            result['user_id'] = user_id
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/email-results', methods=['POST'])
def email_results():
    """Send results to email"""
    try:
        data = request.json
        logger.info(f"Received email request: {data}")
        
        # Extract email and recommendation content from request
        email_address = data.get('email')
        recommendation = data.get('recommendation')
        
        if not email_address or not recommendation:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Call the email function (you'll need to implement this)
        try:
            from tools.email_tool import send_recommendation_email
            success = send_recommendation_email(email_address, recommendation)
            
            if success:
                return jsonify({'success': True, 'message': 'Email sent successfully'})
            else:
                return jsonify({'success': False, 'error': 'Failed to send email'}), 500
                
        except ImportError:
            return jsonify({'error': 'Email functionality not available'}), 501
            
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/track-event', methods=['POST'])
def track_event():
    """Track user interaction events"""
    try:
        data = request.json
        event_type = data.get('eventType')
        event_data = data.get('eventData', {})
        
        logger.info(f"User event tracked: {event_type} - {event_data}")
        
        # Here you could save the event to a database if needed
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoint for scheduled daily recommendations
@app.route('/api/run-daily-recommendations', methods=['POST'])
def run_daily_recommendations():
    """
    Endpoint for EventBridge to trigger daily recommendations at 7 AM CT
    This can be secured with API keys to ensure only authorized services can call it
    """
    # Verify the request with an API key
    api_key = request.headers.get('X-Api-Key')
    expected_api_key = os.environ.get('SCHEDULER_API_KEY')
    
    # Skip API key check if not configured (for development/testing)
    if expected_api_key and (not api_key or api_key != expected_api_key):
        logger.warning("Unauthorized attempt to access scheduled recommendations endpoint")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get all registered users who have provided email addresses
        users = get_all_registered_users()
        
        if not users:
            return jsonify({
                'status': 'completed',
                'message': 'No users with email addresses found',
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info(f"Starting daily recommendations for {len(users)} users")
        
        results = []
        successful = 0
        failed = 0
        
        # Process each user
        for user in users:
            try:
                # Prepare data for recommendation generation
                user_data = {
                    'business_name': user['name'],
                    'business_type': user['type'],
                    'business_email': user['email'],
                    'business_postal_code': user['postal_code'],
                    'business_latitude': user['latitude'],
                    'business_longitude': user['longitude']
                }
                
                # Generate recommendations using existing function
                recommendation = main_sse_function(user_data)
                
                # Send email with recommendations
                from tools.email_tool import send_recommendation_email
                email_sent = send_recommendation_email(
                    user['email'], 
                    recommendation.get('recommendations', {}).get('overview', str(recommendation))
                )
                
                result_status = 'success' if email_sent else 'email_failed'
                
                if email_sent:
                    successful += 1
                else:
                    failed += 1
                
                results.append({
                    'user_id': user['id'],
                    'email': user['email'],
                    'status': result_status
                })
                
                # Add a small delay between processing users to avoid rate limits on APIs
                if len(users) > 10:  # Only add delay if processing many users
                    import time
                    time.sleep(1)
                    
            except Exception as user_error:
                logger.error(f"Error processing user {user['id']}: {str(user_error)}")
                logger.error(traceback.format_exc())
                results.append({
                    'user_id': user['id'],
                    'email': user['email'],
                    'status': 'error',
                    'error': str(user_error)
                })
                failed += 1
        
        return jsonify({
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'total_users': len(users),
            'successful': successful,
            'failed': failed,
            'results': results
        })
        
    except Exception as e:
        logger.exception(f"Error running daily recommendations: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)