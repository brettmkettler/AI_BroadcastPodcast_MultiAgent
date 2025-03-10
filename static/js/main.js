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
            // Decode base64 audio data
            const audioData = atob(data.audio);
            const audioArray = new Uint8Array(audioData.length);
            for (let i = 0; i < audioData.length; i++) {
                audioArray[i] = audioData.charCodeAt(i);
            }
            
            // Convert to AudioBuffer
            const audioBuffer = await audioContext.decodeAudioData(audioArray.buffer);
            
            // Create and configure source
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            
            // Store reference to current audio
            currentAudio = source;
            
            // Play audio
            source.start(0);
            
            // When audio finishes
            source.addEventListener('ended', () => {
                currentAudio = null;
                console.log(`Audio finished for ${data.host}, duration was ${data.duration}s`);
                socket.emit('audio_finished', { host: data.host });
            });
        } catch (error) {
            console.error('Error playing audio:', error);
            // Even if audio fails, notify server to continue conversation
            socket.emit('audio_finished', { host: data.host });
        }
    });

    socket.on('visualization_update', (data) => {
        // Update visualizations based on audio data
        if (data.host1Data) {
            updateWaveform('host1-waveform', data.host1Data);
        }
        if (data.host2Data) {
            updateWaveform('host2-waveform', data.host2Data);
        }
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
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = data.message;
        transcript.appendChild(errorDiv);
        transcript.scrollTop = transcript.scrollHeight;
    });
});

function updateWaveform(elementId, audioData) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw waveform
    ctx.beginPath();
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;

    const step = width / audioData.length;
    for (let i = 0; i < audioData.length; i++) {
        const x = i * step;
        const y = (height / 2) * (1 - audioData[i]);
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }

    ctx.stroke();
}
