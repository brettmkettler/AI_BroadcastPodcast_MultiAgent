document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const transcript = document.getElementById('transcript');
    const currentTopic = document.getElementById('current-topic');
    const topicInput = document.getElementById('topic-input');
    const changeTopic = document.getElementById('change-topic');

    let isRecording = false;
    let audioContext = null;
    let currentAudio = null;

    startButton.addEventListener('click', () => {
        isRecording = true;
        startButton.disabled = true;
        stopButton.disabled = false;
        
        // Initialize audio context on first click (browsers require user interaction)
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const topic = topicInput.value.trim() || undefined;
        socket.emit('start_podcast', { topic });
    });

    stopButton.addEventListener('click', () => {
        isRecording = false;
        startButton.disabled = false;
        stopButton.disabled = true;
        socket.emit('stop_podcast');
    });

    changeTopic.addEventListener('click', () => {
        const newTopic = topicInput.value.trim();
        if (newTopic) {
            socket.emit('change_topic', { topic: newTopic });
        }
    });

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('transcript_update', (data) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'mb-2';
        messageDiv.innerHTML = `<strong>${data.speaker}:</strong> ${data.text}`;
        transcript.appendChild(messageDiv);
        transcript.scrollTop = transcript.scrollHeight;
    });

    socket.on('topic_update', (data) => {
        currentTopic.textContent = data.topic;
        if (topicInput.value.trim() === '') {
            topicInput.value = data.topic;
        }
    });

    socket.on('audio_update', async (data) => {
        try {
            // Convert audio data to AudioBuffer
            const audioBuffer = await audioContext.decodeAudioData(data.audio);
            
            // Create and configure source
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            
            // Store reference to current audio
            currentAudio = source;
            
            // Play audio
            source.start(0);
            
            // When audio finishes
            source.onended = () => {
                currentAudio = null;
                // Notify server that audio finished playing
                socket.emit('audio_finished', { host: data.host });
            };
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    });

    socket.on('visualization_update', (data) => {
        // Update visualizations based on audio data
        updateVisualization(data);
    });

    socket.on('podcast_stopped', (data) => {
        isRecording = false;
        startButton.disabled = false;
        stopButton.disabled = true;
        if (currentAudio) {
            currentAudio.stop();
            currentAudio = null;
        }
    });

    socket.on('error', (data) => {
        console.error('Server error:', data.message);
        // Display error to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = data.message;
        transcript.appendChild(errorDiv);
        transcript.scrollTop = transcript.scrollHeight;
    });
});

// Function to update the audio visualizations
function updateVisualization(data) {
    const { host1Data, host2Data } = data;
    
    // Update waveform displays
    if (host1Data) {
        updateWaveform('waveform1', host1Data);
    }
    if (host2Data) {
        updateWaveform('waveform2', host2Data);
    }
}

function updateWaveform(elementId, audioData) {
    const canvas = document.getElementById(elementId);
    const ctx = canvas.getContext('2d');
    
    // Clear previous drawing
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw new waveform
    ctx.beginPath();
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
    
    const sliceWidth = canvas.width / audioData.length;
    let x = 0;
    
    for (let i = 0; i < audioData.length; i++) {
        const v = audioData[i] / 128.0;
        const y = (v * canvas.height) / 2;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        x += sliceWidth;
    }
    
    ctx.stroke();
}
