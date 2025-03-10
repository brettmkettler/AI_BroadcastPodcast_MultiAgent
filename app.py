from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
import base64
import numpy as np
from threading import Event
from agents.podcast_agent import PodcastAgent
from agents.voice_synthesizer import VoiceSynthesizer
from agents.twitter_broadcaster import TwitterBroadcaster
import time

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

# Create agents
host1 = PodcastAgent(
    name="Brett",
    personality="A witty and knowledgeable tech enthusiast who loves making complex topics accessible",
    voice_id="7eFTSJ6WtWd9VCU4ZlI1"  # Brett
)

host2 = PodcastAgent(
    name="Kimber",
    personality="An insightful and thoughtful analyst who brings fresh perspectives to discussions",
    voice_id="fQ74DTbwd8TiAJFxu9v8"  # Kimber voice
)

voice_synthesizer = VoiceSynthesizer()
twitter_broadcaster = TwitterBroadcaster()

# Store active conversations and their audio events
active_conversations = {}
audio_events = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_podcast')
def handle_start_podcast(data=None):
    # Get topic from client or use default
    topic = data.get('topic') if data else "The Future of AI and Its Impact on Society"
    
    # Clear both agents' memories when starting a new podcast
    host1.clear_memory()
    host2.clear_memory()
    
    # Create an event for this conversation
    conversation_id = request.sid
    audio_events[conversation_id] = Event()
    audio_events[conversation_id].set()  # Initially set to allow first message
    
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
    next_response = None
    next_audio = None
    next_duration = 0
    
    while room in active_conversations:
        try:
            # If we have a queued response from the previous iteration, use it
            if next_response and next_audio:
                response2 = next_response
                audio2 = next_audio
                duration2 = next_duration
                next_response = None
                next_audio = None
                next_duration = 0
            else:
                # Host 2 speaks (first time only)
                response2 = host2.generate_response(current_context)
                audio2, duration2 = voice_synthesizer.synthesize(response2, host2.voice_id)
                if not audio2:
                    raise Exception("Failed to synthesize audio for Host 2")
            
            # While Host 2's audio is being prepared/played, generate Host 1's next response
            response1 = host1.generate_response(response2)
            audio1, duration1 = voice_synthesizer.synthesize(response1, host1.voice_id)
            if not audio1:
                raise Exception("Failed to synthesize audio for Host 1")
            
            # Play Host 2's audio
            socketio.emit('transcript_update', {
                'speaker': host2.name,
                'text': response2,
                'isPlaying': True
            }, room=room)
            
            if audio2:
                # Convert audio bytes to base64 for transmission
                audio_data = base64.b64encode(audio2).decode('utf-8')
                socketio.emit('audio_update', {
                    'audio': audio_data,
                    'host': 'host2',
                    'duration': duration2
                }, room=room)
                
                # For visualization, just use a simple placeholder
                visualization_data = [0.5] * 100
                socketio.emit('visualization_update', {
                    'host2Data': visualization_data
                }, room=room)
                
                # Wait for audio duration plus a buffer
                wait_time = duration2 + 2.0  # Add 2 second buffer
                print(f"Waiting {wait_time:.1f} seconds for Host 2 audio...")
                socketio.sleep(wait_time)
            
            # Update context with host2's response
            current_context = response2
            
            # While Host 1's audio is playing, generate Host 2's next response
            next_response = host2.generate_response(response1)
            next_audio, next_duration = voice_synthesizer.synthesize(next_response, host2.voice_id)
            if not next_audio:
                raise Exception("Failed to synthesize next audio for Host 2")
            
            # Play Host 1's audio
            socketio.emit('transcript_update', {
                'speaker': host1.name,
                'text': response1,
                'isPlaying': True
            }, room=room)
            
            if audio1:
                # Convert audio bytes to base64 for transmission
                audio_data = base64.b64encode(audio1).decode('utf-8')
                socketio.emit('audio_update', {
                    'audio': audio_data,
                    'host': 'host1',
                    'duration': duration1
                }, room=room)
                
                # For visualization, just use a simple placeholder
                visualization_data = [0.5] * 100
                socketio.emit('visualization_update', {
                    'host1Data': visualization_data
                }, room=room)
                
                # Wait for audio duration plus a buffer
                wait_time = duration1 + 0.4  # Add 2 second buffer
                print(f"Waiting {wait_time:.1f} seconds for Host 1 audio...")
                socketio.sleep(wait_time)
            
            # Update context with host1's response
            current_context = response1
            
            # Broadcast highlight to Twitter (X)
            twitter_broadcaster.post_update(f" {host1.name}: '{response1[:50]}...' | {host2.name}: '{response2[:50]}...' #AIpodcast")
            
        except Exception as e:
            print(f"Error in conversation: {str(e)}")
            socketio.emit('error', {'message': f'An error occurred: {str(e)}'}, room=room)
            break

@socketio.on('audio_finished')
def handle_audio_finished(data):
    """Handle when audio finishes playing on the client."""
    if request.sid in audio_events:
        audio_events[request.sid].set()  # Signal that audio is finished

@socketio.on('stop_podcast')
def handle_stop_podcast():
    conversation_id = request.sid
    if conversation_id in active_conversations:
        del active_conversations[conversation_id]
    if conversation_id in audio_events:
        audio_events[conversation_id].set()  # Release any waiting threads
        del audio_events[conversation_id]
    socketio.emit('podcast_stopped', {'message': 'Podcast stopped'}, room=conversation_id)

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
