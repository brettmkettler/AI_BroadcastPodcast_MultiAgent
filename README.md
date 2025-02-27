# AI Podcast Broadcaster

An interactive AI-powered podcast system that creates dynamic conversations between two AI agents and broadcasts them to X (Twitter) with real-time visualization.

## Features

- Two AI podcast hosts with distinct personalities
- Real-time voice synthesis using Eleven Labs
- Live audio streaming and broadcasting to X
- Interactive visualization of the conversation
- Real-time audio waveform display

## Requirements

- Python 3.8+
- Eleven Labs API key
- X (Twitter) API credentials
- Modern web browser

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
ELEVENLABS_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_ACCESS_TOKEN=your_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Configuration

- Modify the AI personalities in `config/personalities.py`
- Adjust visualization settings in `static/js/visualization.js`
- Configure podcast topics in `config/topics.py`
