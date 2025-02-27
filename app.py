from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from agents.podcast_agent import PodcastAgent
from agents.voice_synthesizer import VoiceSynthesizer
from agents.twitter_broadcaster import TwitterBroadcaster

load_dotenv()

# Check for required environment variables
required_env_vars = [
    'ELEVENLABS_API_KEY',
    'OPENAI_API_KEY',
    'VOICE_ID_HOST1',
    'VOICE_ID_HOST2'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please set them in your .env file.")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app, async_mode='eventlet')

# Initialize agents
host1 = PodcastAgent(
    name="Brett",
    personality="A tech-savvy, enthusiastic AI host who loves discussing emerging technologies and their impact on society.",
    voice_id=os.getenv('VOICE_ID_HOST1')
)

host2 = PodcastAgent(
    name="Kimber",
    personality="A thoughtful, analytical AI host with a background in philosophy and ethics, offering deep insights into technological implications.",
    voice_id=os.getenv('VOICE_ID_HOST2')
)

voice_synthesizer = VoiceSynthesizer()
twitter_broadcaster = TwitterBroadcaster()

# Store active conversations
active_conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    # Clean up any active conversations for this client
    if request.sid in active_conversations:
        del active_conversations[request.sid]

@socketio.on('start_podcast')
def handle_start_podcast(data=None):
    # Get topic from client or use default
    topic = data.get('topic') if data else "The Future of AI and Its Impact on Society"
    
    # Clear both agents' memories when starting a new podcast
    host1.clear_memory()
    host2.clear_memory()
    
    socketio.emit('topic_update', {'topic': topic}, room=request.sid)
    
    # Start the conversation
    active_conversations[request.sid] = True
    socketio.start_background_task(
        target=run_podcast_conversation,
        topic=topic,
        room=request.sid
    )

def run_podcast_conversation(topic, room):
    current_context = f"Topic: {topic}\nLet's start a friendly and engaging discussion about {topic}."
    
    while room in active_conversations:
        try:
            # Host 1 speaks
            response1 = host1.generate_response(current_context)
            audio1 = voice_synthesizer.synthesize(response1, host1.voice_id)
            
            # Emit transcript and audio data
            socketio.emit('transcript_update', {
                'speaker': host1.name,
                'text': response1,
                'isPlaying': True
            }, room=room)
            
            if audio1:
                socketio.emit('audio_update', {
                    'audio': audio1,
                    'host': 'host1'
                }, room=room)
                socketio.emit('visualization_update', {
                    'host1Data': audio1.get_audio_data()
                }, room=room)
                
                # Wait for client to confirm audio finished
                socketio.sleep(0.1)  # Small delay to ensure smooth playback
            
            # Update context with host1's response
            current_context = response1
            
            # Host 2 speaks
            response2 = host2.generate_response(current_context)
            audio2 = voice_synthesizer.synthesize(response2, host2.voice_id)
            
            socketio.emit('transcript_update', {
                'speaker': host2.name,
                'text': response2,
                'isPlaying': True
            }, room=room)
            
            if audio2:
                socketio.emit('audio_update', {
                    'audio': audio2,
                    'host': 'host2'
                }, room=room)
                socketio.emit('visualization_update', {
                    'host2Data': audio2.get_audio_data()
                }, room=room)
                
                # Wait for client to confirm audio finished
                socketio.sleep(0.1)  # Small delay to ensure smooth playback
            
            # Update context with host2's response
            current_context = response2
            
            # Broadcast highlight to Twitter (X)
            twitter_broadcaster.post_update(f" {host1.name}: '{response1[:50]}...' | {host2.name}: '{response2[:50]}...' #AIpodcast")
            
        except Exception as e:
            print(f"Error in conversation: {str(e)}")
            socketio.emit('error', {'message': 'An error occurred in the conversation'}, room=room)
            break

@socketio.on('stop_podcast')
def handle_stop_podcast():
    if request.sid in active_conversations:
        del active_conversations[request.sid]
    socketio.emit('podcast_stopped', {'message': 'Podcast stopped'}, room=request.sid)

@socketio.on('change_topic')
def handle_topic_change(data):
    topic = data.get('topic')
    if topic:
        # Clear memories when changing topics
        host1.clear_memory()
        host2.clear_memory()
        socketio.emit('topic_update', {'topic': topic}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
