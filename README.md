# Gmail Chat Assistant

A modern web application that allows you to interact with your Gmail inbox using natural language. Built with FastAPI and featuring a beautiful chat interface, this application helps you query and analyze your emails through simple conversations.

## Features

- 🤖 Natural language processing for email queries
- 💬 Modern, responsive chat interface
- 🔍 Smart email search and analysis
- ⚡ Real-time responses
- 📱 Mobile-friendly design
- ⌨️ Support for multi-line messages
- ⏳ Typing indicators for better UX

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail API enabled
- Google API credentials (OAuth 2.0)

## Setup

### 1. Enable Gmail API

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable Gmail API:
   - Go to APIs & Services > Library
   - Search for "Gmail API"
   - Click "Enable"
4. Configure OAuth consent screen:
   - Go to OAuth consent screen
   - Choose "External" user type (recommended for development)
   - Fill in the required information
5. Create OAuth credentials:
   - Go to Credentials > Create Credentials > OAuth client ID
   - Choose "Desktop App" as application type
   - Download the credentials.json file
   - Place it in your project root directory

### 2. Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gmail-chat-assistant
```

2. Create and activate virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Unix/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Google API credentials:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. First Run Configuration

1. On first run, the application will:
   - Open your default browser
   - Ask for Gmail login
   - Request necessary permissions
   - Generate a token.json file for future use

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

## Usage

1. The chat interface will open with a welcome message
2. Type your query in natural language, for example:
   - How much did I spend on Zomato in year 2025??
   - What did I order most on Zomato in year 2025??
   - How much did I spent on Swiggy in year 2025??
   - How much did I spent in Taara Kitchen in May 2025??
   - where did I travel using Redbus in year 2025??
   - How much did I spent on SHAIK JABEER in year 2025??
   - when did I last pay for ChatGPT subscription in year 2025??
   - when did I last pay for Cursor subscription in year 2025??
   - when did I buy Apple iphone 13 from Croma??
   - when did I buy Samsung phone from Flipkart??
   - when did I buy Redmi Note 5 Pro??
   - When did I last go to Karachi Bakery??
   - What meetings were scheduled in year 2025 excluding ERA V3 and EAG V1?
   - When did I give interviews to Harman??
3. Press Enter or click the send button to submit your query
4. The assistant will process your request and display the results in a chat bubble

## Project Structure

```
gmail-chat-assistant/
├── main.py              # FastAPI application and routes
├── gmail_utils.py       # Gmail API integration
├── gemini_agent.py      # Natural language processing
├── requirements.txt     # Project dependencies
├── static/             # Static files
│   ├── style.css      # CSS styles
│   └── script.js      # Frontend JavaScript
└── templates/          # HTML templates
    └── index.html     # Main chat interface
```

## Technologies Used

- Backend:
  - FastAPI
  - Google Gmail API
  - Google Gemini AI
  - Python-dotenv

- Frontend:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)
  - Inter font family

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
