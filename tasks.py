from crewai import Task
from textwrap import dedent

class AdvertisingTasks:
    def __tip_section(self):
        return "If you do an EXCEPTIONAL job with your analysis, the small business could see a 300% increase in customer traffic!"

    def collect_events_data(self, agent, business_postal_code):
        """Task for collecting event data for the specified postal code"""
        return Task(
            description=dedent(
                f"""
                Collect and analyze event data for postal code {business_postal_code} and the surrounding area.
                
                You need to:
                1. Get today's events happening in the postal code area
                2. Get events from the past week in the postal code area
                3. Analyze the types of events, their popularity, and potential audience
                4. Identify patterns or special events that might influence consumer behavior
                5. Determine if there are more or fewer events than usual
                6. Create a summary of the event landscape that would be relevant to small businesses
                
                {self.__tip_section()}
                
                Make sure to include specific event details that would be most relevant to small 
                businesses like restaurants, coffee shops, ice cream parlors, and other local retail.
            """
            ),
            expected_output="A comprehensive analysis of local events with insights on how they might impact small business traffic and advertising opportunities",
            agent=agent,
        )

    def analyze_weather_conditions(self, agent, latitude, longitude):
        """Task for analyzing weather conditions for a specific location"""
        return Task(
            description=dedent(
                f"""
                Analyze the weather forecast for the location at latitude {latitude} and longitude {longitude}.
                
                You need to:
                1. Get the current weather forecast for the location
                2. Analyze how the weather conditions might affect consumer behavior
                3. Identify weather patterns that create opportunities for specific businesses
                    (e.g., hot weather is good for ice cream shops, rainy weather might benefit coffee shops)
                4. Determine if there are any unusual or extreme weather conditions that businesses should be aware of
                5. Create a summary of how the weather might influence foot traffic and purchasing decisions
                
                {self.__tip_section()}
                
                Focus on weather factors that would directly impact small businesses like restaurants,
                coffee shops, ice cream parlors, and other local retail.
            """
            ),
            expected_output="A detailed weather analysis with specific insights on how current and upcoming conditions will affect consumer behavior and create business opportunities",
            agent=agent,
        )

    def create_advertising_recommendation(self, agent, events_analysis, weather_analysis, business_type, business_name, business_email):
        """Task for creating an advertising recommendation based on events and weather data"""
        return Task(
            description=dedent(
                f"""
                Create a comprehensive advertising recommendation for {business_name} (a {business_type}) based on
                the events analysis and weather forecast.
                
                You need to:
                1. Review the events analysis and identify key opportunities
                2. Analyze the weather forecast and its potential impact on {business_type} businesses
                3. Combine these insights to determine if conditions are favorable for Google Ads advertising
                4. If favorable, provide specific recommendations for advertising strategy:
                    - Best times to run ads
                    - Suggested ad messaging that ties to current events or weather
                    - Target audiences based on nearby events
                5. If conditions are unfavorable, explain why advertising might not be effective right now
                6. Create a clear, concise recommendation with supporting evidence
                7. Send this recommendation via email to {business_email}
                
                {self.__tip_section()}
                
                Your recommendation should be data-driven, specific to {business_type} businesses,
                and provide clear actionable advice that the business owner can immediately implement.
            """
            ),
            expected_output="A detailed advertising recommendation with clear reasoning and specific action items, delivered by email to the business owner",
            agent=agent,
        )
