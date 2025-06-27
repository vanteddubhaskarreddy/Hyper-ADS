import os
import sys
import traceback
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import CrewAI - our mock ChromaDB will make this work
from crewai import Crew, Process, Task

# Rest of your imports
from decouple import config

# Import agent modules
from agents_sse import AdvertisingAgents
from tasks import AdvertisingTasks
from tools.events_tool_crewai import EventsTool


class AdvertisingAdvisorCrew:
    def __init__(self, business_name, business_type, business_postal_code, 
                business_latitude, business_longitude, business_email):
        """Initialize the Advertising Advisor Crew with business details"""
        self.business_name = business_name
        self.business_type = business_type
        self.business_postal_code = business_postal_code
        self.business_latitude = business_latitude
        self.business_longitude = business_longitude
        self.business_email = business_email
        # Get Gemini API key from environment or .env file
        self.gemini_api_key = os.environ.get("GOOGLE_API_KEY") or config("GOOGLE_API_KEY")

    def run(self, stream=False):
        """Run the advertising advisor crew workflow"""
        # Initialize agents and tasks
        agents = AdvertisingAgents(self.gemini_api_key)
        tasks = AdvertisingTasks()
        
        # Get event data directly (since tools aren't working with this CrewAI version)
        logger.info("Fetching event data from database...")
        
        try:
            # Use separate EventsTool instances to avoid connection reuse issues
            events_tool_1 = EventsTool()
            todays_events = events_tool_1.get_todays_events(self.business_postal_code)
            
            # Add delay to ensure proper connection cleanup
            import time
            time.sleep(2)
            
            # Use separate instance for second call
            events_tool_2 = EventsTool()
            recent_events = events_tool_2.get_events_by_postal_code(self.business_postal_code, 7)
            
            events_data = f"Today's Events:\n{todays_events}\n\nRecent Events (Past 7 Days):\n{recent_events}"
            logger.info("Event data retrieved successfully.")
        except Exception as e:
            logger.warning(f"Could not fetch event data: {e}")
            events_data = f"Unable to fetch event data for postal code {self.business_postal_code}. Please analyze based on general business insights."
        
        # Get weather data directly
        logger.info("Fetching weather data from MCP server...")
        try:
            from tools.weather_tool_sse import MCPSSEWeatherTool
            weather_tool = MCPSSEWeatherTool()
            weather_coords = f"{self.business_latitude},{self.business_longitude}"
            weather_data = weather_tool._run(weather_coords)
            logger.info("Weather data retrieved successfully.")
        except Exception as e:
            logger.warning(f"Could not fetch weather data: {e}")
            weather_data = f"Unable to fetch weather data for coordinates {self.business_latitude},{self.business_longitude}. Please analyze based on general weather patterns."
        
        # Create the agents
        data_analyst = agents.data_analyst()
        weather_analyst = agents.weather_analyst()
        marketing_strategist = agents.marketing_strategist()
        
        # Create the tasks with event data included
        # Summarize events data to reduce input length
        events_summary = self._summarize_events_data(events_data)
        
        collect_events = Task(
            description=f"""
            Analyze the following event summary for postal code {self.business_postal_code}:
            
            {events_summary}
            
            Your task is to:
            1. Analyze the types of events and their potential audience
            2. Identify patterns that might influence consumer behavior
            3. Create insights relevant to small businesses like {self.business_type}
            
            Focus on actionable insights for {self.business_name} ({self.business_type}).
            """,
            expected_output="A comprehensive analysis of local events with insights on how they might impact small business traffic and advertising opportunities",
            agent=data_analyst,
        )
        
        analyze_weather = Task(
            description=f"""
            Analyze weather conditions for {self.business_name} at coordinates {self.business_latitude}, {self.business_longitude}:
            
            Weather Data: {weather_data[:300]}...
            
            Your task is to:
            1. Analyze how weather affects {self.business_type} customer behavior
            2. Identify opportunities or challenges from current conditions
            3. Provide specific weather-based recommendations
            
            Keep analysis focused and concise.
            """,
            expected_output="A detailed weather analysis with specific insights on how current and upcoming conditions will affect consumer behavior and create business opportunities",
            agent=weather_analyst,
        )
        
        create_recommendation = Task(
            description=f"""
    Create advertising recommendation for {self.business_name} ({self.business_type}) based on:
    - Events analysis from data analyst
    - Weather analysis from weather analyst
    
    Your response will be sent directly as an HTML email, so use proper HTML tags for formatting:
    1. Use <h3> tags for headings (e.g., <h3>Should we advertise now?</h3>)
    2. Use <b> tags for bold text
    3. Use <ul> and <li> tags for bullet points
    4. Use <p> tags for paragraphs

    If there are no events, provide a general analysis based on the business type and weather conditions, 
    and mention that the event data will be refreshed tomorrow and will get an email with the new data.

    Your response will be delivered to the user. Structure your response clearly with:
    - Begin with a proper salutation: "Dear {self.business_name} Team,"
    - Include these sections with proper headings:
        - "Should we advertise now?" (Yes/No with brief reason)
        - "Best times, messaging, target audience" (if yes)
        - "Why wait and when to revisit" (if no)
    
    Keep response concise and actionable. Don't exceed 200 words.
    Only analyze for today. The event data provided is for today and past 7 days.
    Compare with the past events data and determine whether to advertise today or not.
    Analyze the events and weather data and provide recommendations if the event members are likely to visit the business today.
    End with a friendly closing:
    <p>Hope this helps!<br>
    Best regards,<br>
    Hyper ADS team :)</p>
    """,
            expected_output="A detailed advertising recommendation with clear reasoning and specific action items",
            agent=marketing_strategist,
        )
        
        # Create the crew
        crew = Crew(
            agents=[data_analyst, weather_analyst, marketing_strategist],
            tasks=[collect_events, analyze_weather, create_recommendation],
            embedder={
                "provider": "groq",
                "config": {
                    "model": 'groq/llama3-70b-8192'
                }
            },
            verbose=True,
            process=Process.sequential  # Run tasks sequentially to ensure data flows correctly
        )
        
        # Run the crew and return the results
        result = crew.kickoff()
        
        # Send the recommendation via email if email is provided
        if self.business_email:
            logger.info(f"Sending recommendation via email to {self.business_email}...")
            try:
                from tools.email_tool import EmailTool
                email_tool = EmailTool()
                email_subject = f"Advertising Recommendation for {self.business_name}"
                email_result = email_tool.send_email(self.business_email, email_subject, str(result))
                logger.info(f"Email status: {email_result}")
            except Exception as e:
                logger.warning(f"Could not send email: {e}")
        
        # Structure the output for web display
        formatted_result = {
            "recommendations": {
                "overview": str(result),
                "should_advertise": "Yes" if "yes" in str(result).lower() else "No",
                "channels": self._extract_channels_from_result(str(result))
            }
        }
        
        return formatted_result

    def _summarize_events_data(self, events_data):
        """Summarize event data to reduce input length for LLM"""
        lines = events_data.split('\n')
        
        # Extract just the key info
        today_events = []
        recent_events = []
        current_section = None
        
        for line in lines:
            if "Today's Events:" in line:
                current_section = "today"
                continue
            elif "Recent Events" in line:
                current_section = "recent"
                continue
            elif line.startswith("Event:"):
                event_name = line.replace("Event: ", "").strip()
                if current_section == "today":
                    today_events.append(event_name)
                elif current_section == "recent":
                    recent_events.append(event_name)
        
        # Create summary
        summary = f"""
Event Summary for Postal Code {self.business_postal_code}:

Today's Events ({len(today_events)} total):
{', '.join(today_events[:5])}{'...' if len(today_events) > 5 else ''}

Recent Events ({len(recent_events)} total in past 7 days):
{', '.join(recent_events[:5])}{'...' if len(recent_events) > 5 else ''}

Event Types Identified:
- Entertainment/Gaming: Scavenger hunts, escape rooms, tours
- Professional: AI training, leadership workshops  
- Social: Date nights, matchmaking events
- Food/Beverage: Sip & glaze experiences

Key Venues: 300 W 13th St, Made in KC Cafe, Regus Downtown, River Bluff Brewing
        """
        
        return summary.strip()

    def _extract_channels_from_result(self, result):
        """Extract recommended channels from the result text"""
        channels = []
        
        # Check for common advertising platforms
        if "facebook" in result.lower():
            channels.append({
                "name": "Facebook Ads",
                "description": "Target local audiences with demographic precision",
                "budget": 300
            })
        
        if "instagram" in result.lower():
            channels.append({
                "name": "Instagram",
                "description": "Visual marketing for younger audiences",
                "budget": 250
            })
        
        if "google" in result.lower():
            channels.append({
                "name": "Google Ads",
                "description": "Search and display advertising with keyword targeting",
                "budget": 400
            })
        
        if "local" in result.lower():
            channels.append({
                "name": "Local Partnerships",
                "description": "Collaborate with local event organizers",
                "budget": 200
            })
        
        # Add a default option if no specific channels detected
        if not channels:
            channels.append({
                "name": "Digital Marketing Mix",
                "description": "Balanced approach across multiple platforms",
                "budget": 500
            })
            
        return channels

# Function to handle web requests
def main(params, stream=False):
    """Main function to process web requests"""
    try:
        # Extract parameters from the web request
        business_name = params.get('business_name', '')
        business_type = params.get('business_type', '')
        business_email = params.get('business_email', '')
        
        # Set default values for target_audience and budget
        target_audience = "General consumers in the local area"  # Default value
        budget = 1000  # Default budget value
        
        # Use default postal code and coordinates if not provided
        business_postal_code = params.get('business_postal_code', '66213')
        
        # Format coordinates to exactly 4 decimal places
        business_latitude = params.get('business_latitude')
        business_longitude = params.get('business_longitude')
        
        if business_latitude is not None:
            business_latitude = float("{:.4f}".format(float(business_latitude)))
        else:
            business_latitude = 38.9041  # Default with 4 decimal places
            
        if business_longitude is not None:
            business_longitude = float("{:.4f}".format(float(business_longitude)))
        else:
            business_longitude = -94.6898  # Default with 4 decimal places
        
        logger.info(f"Processing request for {business_name} ({business_type})")
        logger.info(f"Using coordinates: {business_latitude}, {business_longitude}")
        
        # Create and run the crew with CrewAI
        crew = AdvertisingAdvisorCrew(
            business_name,
            business_type,
            business_postal_code,
            business_latitude,
            business_longitude,
            business_email
        )
        
        result = crew.run(stream=stream)
        return result
        
    except Exception as e:
        logger.exception("Error in main function")
        return {"error": str(e), "traceback": traceback.format_exc()}

# End of file