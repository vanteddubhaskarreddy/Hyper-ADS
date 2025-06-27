import asyncio
import json
import os
from typing import Optional, Dict, Any, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from mcp import ClientSession
from mcp.client.sse import sse_client


class WeatherToolInput(BaseModel):
    """Input schema for the weather tool"""
    location: str = Field(description="Location for weather data. Use 'latitude,longitude' for forecast or 'STATE' for alerts (e.g., '39.0997,-94.5786' or 'MO')")


class MCPSSEWeatherTool(BaseTool):
    """Weather tool that connects to MCP server via SSE"""
    
    name: str = "get_weather"
    description: str = "Get weather forecast or alerts for a location. Use 'latitude,longitude' for forecast or 'STATE' for alerts."
    args_schema: Type[BaseModel] = WeatherToolInput
    
    # Define server_url as a proper field
    server_url: str = Field(default="https://ptk4g7rrkh.us-east-2.awsapprunner.com", description="MCP server URL")

    def __init__(self, server_url: str = "https://ptk4g7rrkh.us-east-2.awsapprunner.com", **kwargs):
        super().__init__(server_url=server_url, **kwargs)

    async def _call_tool_with_fresh_connection(self, tool_name: str, args: dict) -> str:
        """Call a tool with a fresh connection that gets cleaned up immediately"""
        try:
            sse_url = f"{self.server_url}/sse"
            
            # Use the SSE client context manager directly
            async with sse_client(sse_url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, args)
                    return result.content if hasattr(result, 'content') else str(result)
                    
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"

    def _run(self, location: str) -> str:
        """Run the weather tool synchronously"""
        return asyncio.run(self._run_async(location))

    async def _run_async(self, location: str) -> str:
        """Run the weather tool asynchronously"""
        try:
            # Determine if location is coordinates or state code
            if ',' in location:
                # Parse coordinates
                try:
                    lat_str, lon_str = location.split(',')
                    latitude = float(lat_str.strip())
                    longitude = float(lon_str.strip())
                    
                    # Call forecast tool
                    args = {"latitude": latitude, "longitude": longitude}
                    result = await self._call_tool_with_fresh_connection("get_forecast", args)
                    return f"Weather forecast for coordinates ({latitude}, {longitude}):\n{result}"
                    
                except ValueError:
                    return f"Error: Invalid coordinates format. Use 'latitude,longitude' (e.g., '39.0997,-94.5786')"
            
            else:
                # Assume it's a state code
                state = location.strip().upper()
                if len(state) != 2:
                    return "Error: State code must be exactly 2 letters (e.g., 'MO', 'CA')"
                
                # Call alerts tool
                args = {"state": state}
                result = await self._call_tool_with_fresh_connection("get_alerts", args)
                return f"Weather alerts for {state}:\n{result}"
                
        except Exception as e:
            return f"Error processing weather request: {str(e)}"

    def execute(self, data):
        """Execute the weather tool with data from request"""
        # Try to use latitude and longitude from input data if available
        latitude = data.get('business_latitude')
        longitude = data.get('business_longitude')
        
        if latitude is not None and longitude is not None:
            # Format to exactly 4 decimal places
            formatted_lat = "{:.4f}".format(float(latitude))
            formatted_lon = "{:.4f}".format(float(longitude))
            location = f"{formatted_lat},{formatted_lon}"
        else:
            # Fall back to postal code or default location
            postal_code = data.get('business_postal_code', '66213')
            # You could add geocoding here to convert postal code to coordinates
            # For now, use a default location based on postal code
            if postal_code == '66213':
                location = "38.9041,-94.6898"  # Coordinates for 66213 (formatted to 4 decimals)
            else:
                # Use a generic format for other postal codes
                location = f"{postal_code}"
    
        # Now use the location for the weather API
        try:
            return self._run(location)
        except Exception as e:
            return f"Error getting weather data: {str(e)}"


# Helper function to create the tool instance
def create_weather_tool(server_url: str = "https://ptk4g7rrkh.us-east-2.awsapprunner.com") -> MCPSSEWeatherTool:
    """Create and return a weather tool instance"""
    return MCPSSEWeatherTool(server_url=server_url)


# Example usage and testing
if __name__ == "__main__":
    async def test_tool():
        tool = MCPSSEWeatherTool()
        
        print("Testing weather tool with coordinates (Kansas City):")
        result = await tool._run_async("39.0997,-94.5786")
        print(f"Result: {result}\n")
        
        print("Testing weather tool with state code (Missouri alerts):")
        result = await tool._run_async("MO")
        print(f"Result: {result}\n")
    
    # Test the tool
    asyncio.run(test_tool())