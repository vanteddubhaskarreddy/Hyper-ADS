# 🎯 Advertising Advisor AI

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-App%20Runner-orange?style=flat-square&logo=amazon-aws)
![AI](https://img.shields.io/badge/AI-Gemini-purple?style=flat-square&logo=google)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue?style=flat-square&logo=postgresql)

An intelligent, agentic AI system that helps small businesses make data-driven advertising decisions by analyzing local events and weather conditions.


## 📋 Table of Contents

- Overview
- System Architecture
- Features
- Components
- Prerequisites
- Installation
- Configuration
- Usage
- Project Structure
- Technologies Used
- License

## 🔭 Overview

The Advertising Advisor AI is a sophisticated platform that transforms how small businesses approach advertising. By analyzing local events and weather patterns, the system generates personalized, actionable marketing recommendations that are delivered directly to business owners' inboxes each morning.

Instead of relying on intuition or complicated marketing platforms, small business owners receive clear guidance like:

> "Today, promote your iced coffee specials between 1-4 PM. There's a festival happening 2 blocks away with 500+ attendees, and temperatures will reach 85°F. Target festival-goers with a 'cool down' message."

## 🏗 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ EventBrite Data │    │   Weather Data   │    │  Business Data   │
│ (Lambda Scraper)│    │   (MCP Server)   │    │ (User Profiles)  │
└────────┬────────┘    └─────────┬────────┘    └────────┬─────────┘
         │                       │                      │
         ▼                       ▼                      ▼
┌────────────────────────────────────────────────────────────────┐
│                      AWS RDS PostgreSQL                        │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    Advertising Advisor AI                      │
│                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │   Data Analyst  │  │ Weather Analyst │  │    Marketing   │  │
│  │      Agent      │──▶│      Agent      │──▶│  Strategist   │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                Email Recommendations Delivery                  │
└────────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **🤖 Intelligent AI Agents** - Three specialized AI agents (Data Analyst, Weather Analyst, and Marketing Strategist) work together to generate recommendations
- **📊 Event Analysis** - Processes local event data to identify high-opportunity timeframes for advertising
- **☁️ Weather Integration** - Incorporates weather forecasts to suggest weather-appropriate marketing tactics
- **🎯 Targeted Recommendations** - Provides business-specific advice based on business type and location
- **📱 Real-time Processing** - Server-Sent Events (SSE) enable live progress tracking during recommendation generation
- **📧 Automated Delivery** - Sends personalized recommendations via email at 7 AM daily
- **⚡ On-demand Analysis** - Generate ad recommendations whenever needed through the web interface
- **📈 Performance Metrics** - Processing 12,000+ events monthly with sub-200ms query response times

## 🧩 Components

The system consists of three main components:

### 1. Main Application (Advertising Advisor)

The core application that orchestrates the AI agents, processes data, and delivers recommendations. Built with Flask, CrewAI, and Google Gemini models.

### 2. EventBrite Lambda Scraper

```python
# Sample code from the EventBrite Lambda scraper
def scrape_events(postal_code):
    """Scrape events for a specific postal code from EventBrite"""
    url = f"https://www.eventbrite.com/d/united-states--{postal_code}/all-events/"
    response = requests.get(url, headers=HEADERS)
    events = parse_events_from_html(response.text)
    return process_events(events)
```

An AWS Lambda function that runs daily at 1 AM CT to scrape upcoming events from EventBrite. The function cleans and processes the data before storing it in the RDS PostgreSQL database.

### 3. Weather MCP Server

```python
@tool("get_weather_forecast")
async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Get the weather forecast for a specific location."""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={api_key}&units=imperial"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
    # Process forecast data
    return format_weather_forecast(data)
```

A Model Context Protocol (MCP) server deployed on AWS App Runner that provides weather data and forecasts. The MCP server communicates with weather APIs and formats the data for AI agent consumption.

## 🔧 Prerequisites

- Google Gemini API key
- Access to the deployed AWS App Runner services:
  - Weather MCP server
  - Main Advertising Advisor application
- Access to AWS RDS PostgreSQL database (for development)
- (Optional) SMTP email credentials for sending recommendations

## 📦 Installation

For local development:

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a .env file based on the `.env.template`:

```bash
cp .env.template .env
# Edit the .env file with your credentials
```

## ⚙️ Configuration

Configure your local environment:

1. Update the MCP server URL in your .env file:
   ```
   WEATHER_MCP_URL=https://your-weather-mcp-server.awsapprunner.com
   ```

2. Configure database connection (default values are pre-configured):
   ```
   DB_HOST=your-rds-hostname.amazonaws.com
   DB_NAME=events_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

3. Configure email settings:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SENDER_EMAIL=your_email@gmail.com
   ```

4. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

## 🚀 Usage

### Web Interface

Access the deployed application at your App Runner URL:
```
https://your-advertising-advisor.awsapprunner.com
```

### Register Your Business

1. Fill out the registration form with:
   - Business name
   - Business type
   - Postal code
   - Email address

2. The system will:
   - Process your information
   - Generate recommendations
   - Send them to your email


## 📁 Project Structure

```
advertising-advisor/
├── app.py                  # Flask web application
├── main_sse.py             # Server-Sent Events implementation
├── agents_sse.py           # AI agent definitions
├── tools/                  # Agent tools
│   ├── weather_tool.py     # Weather data access tools
│   ├── events_tool.py      # Event data access tools
│   ├── email_tool.py       # Email sending tools
│   └── utils.py            # Utility functions
├── templates/              # HTML templates
│   ├── index.html          # Landing page
│   ├── register.html       # Registration form
│   └── processing.html     # Real-time processing page
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
├── eventbrite-lambda/      # Lambda function for event scraping
│   ├── lambda_function.py  # Main Lambda entry point
│   └── requirements.txt    # Lambda dependencies
├── my-mcp-server/          # Weather MCP server
│   ├── server.py           # MCP server implementation
│   ├── tools/              # MCP tools definitions
│   └── requirements.txt    # MCP server dependencies
├── requirements.txt        # Main application dependencies
├── .env.template           # Environment variables template
└── README.md               # This file
```

## 🔧 Technologies Used

<table>
  <tr>
    <td align="center"><img src="https://simpleicons.org/icons/python.svg" width="50px" /><br />Python</td>
    <td align="center"><img src="https://simpleicons.org/icons/flask.svg" width="50px" /><br />Flask</td>
    <td align="center"><img src="https://simpleicons.org/icons/googlecloud.svg" width="50px" /><br />Gemini AI</td>
    <td align="center"><img src="https://simpleicons.org/icons/postgresql.svg" width="50px" /><br />PostgreSQL</td>
  </tr>
  <tr>
    <td align="center"><img src="https://simpleicons.org/icons/amazonaws.svg" width="50px" /><br />AWS App Runner</td>
    <td align="center"><img src="https://simpleicons.org/icons/awslambda.svg" width="50px" /><br />AWS Lambda</td>
    <td align="center"><img src="https://simpleicons.org/icons/amazonrds.svg" width="50px" /><br />AWS RDS</td>
    <td align="center"><img src="https://simpleicons.org/icons/docker.svg" width="50px" /><br />Docker</td>
  </tr>
</table>

- **AI and Machine Learning**
  - Google Gemini Models
  - CrewAI Framework
  - Agentic AI Design
  - Model Context Protocol (MCP)

- **Backend & Data Processing**
  - Python 3.9+
  - Flask & Gunicorn
  - Asynchronous Programming
  - Server-Sent Events (SSE)
  - PostgreSQL Database

- **Cloud Infrastructure**
  - AWS App Runner
  - AWS Lambda
  - AWS RDS (PostgreSQL)
  - AWS EventBridge
  - Docker Containerization
