import os
from crewai import Agent, LLM
from textwrap import dedent
from langchain_google_genai import ChatGoogleGenerativeAI
from decouple import config

# Define the agents for our advertising recommendation system using SSE-based weather tool
class AdvertisingAgents:
    def __init__(self, gemini_api_key):
        model_name = os.environ.get("GEMINI_MODEL_NAME") or config("GEMINI_MODEL_NAME")
        # print(f"🔍 Debug: Using model: {model_name}")  # Debug line to see what model is being used
        # # Initialize Gemini LLM with the provided API key
        # self.gemini = ChatGoogleGenerativeAI(
        #     # model="gemini/gemini-2.0-flash",  # Using the Gemini Flash model for most free API calls
        #     model=model_name,
        #     google_api_key=gemini_api_key,
        #     temperature=0.7  # Lower temperature for more consistent outputs
        # )
        self.gemini = LLM(
            model = model_name,
            api_key = gemini_api_key
        )

    def data_analyst(self):
        """Creates a Data Analyst agent responsible for collecting and analyzing event data"""
        return Agent(
            role="Data Analyst",
            backstory=dedent(f"""
                You are a skilled data analyst specializing in local business trends and event analysis.
                You have a talent for identifying patterns in event data and extracting actionable insights.
                Your expertise lies in synthesizing information about local events, attendance patterns, and 
                consumer behavior to identify business opportunities.
                
                You have access to a PostgreSQL database containing event data. You can analyze events
                happening today and recent events in specific postal codes to provide insights for businesses.
            """),
            goal=dedent(f"""
                Collect and analyze event data to identify patterns and opportunities
                for small businesses. Determine which events indicate high potential for customer engagement
                and business growth. Since you don't have direct database tools, focus on providing
                strategic analysis based on the event information provided in your tasks.
            """),
            verbose=True,            llm=self.gemini,
        )

    def weather_analyst(self):
        """Creates a Weather Analyst agent responsible for analyzing weather conditions"""
        return Agent(
            role="Weather Analyst",
            backstory=dedent(f"""
                You are an expert meteorologist with extensive experience in analyzing weather data and its 
                impact on consumer behavior and business performance. You understand how weather affects 
                different types of businesses and can predict customer behavior based on weather conditions.
                
                You have access to weather forecast data from a reliable weather service. You can analyze
                current and upcoming weather conditions to provide insights for business advertising decisions.
            """),
            goal=dedent(f"""
                Analyze weather forecasts to determine the optimal conditions for advertising different 
                types of small businesses. Identify weather patterns that present unique opportunities 
                for specific business types. Since you don't have direct weather tools, focus on analyzing
                the weather data provided in your tasks.
            """),
            verbose=True,
            llm=self.gemini,
        )

    def marketing_strategist(self):
        """Creates a Marketing Strategist agent responsible for making advertising recommendations"""
        return Agent(
            role="Marketing Strategist",
            backstory=dedent(f"""
                You are a seasoned marketing strategist with a focus on small businesses. You have helped 
                hundreds of small businesses optimize their advertising spend and increase customer traffic. 
                You have a particular expertise in contextual advertising and know exactly when and where 
                businesses should advertise based on events and conditions.
            """),
            goal=dedent(f"""
                Create highly effective advertising recommendations for small businesses based on local 
                events and weather conditions. Determine the optimal advertising strategy, including 
                timing and messaging, to maximize return on advertising investment. Focus on creating
                clear, actionable recommendations that can be immediately implemented.
            """),
            allow_delegation=True,  # Allow the strategist to delegate tasks to other agents
            verbose=True,
            llm=self.gemini,
        )
