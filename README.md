# Team-Music-Player

**Team-Music-Player** is a collaborative music player that allows team members to add or remove songs from a shared queue, making it easy for everyone to control the music without relying on the person connected to the speaker. Perfect for team environments where multiple people want to control the music in real-time.

## Features

- **Search**: Find songs by name using the YouTube Music API.
- **Queue Management**: Add or remove songs from the queue.
- **Playback**: Play songs from the queue automatically without needing constant requests to the person connected to the speaker.
- **Collaborative**: Team members can control the playlist without interrupting the music.

## How It Works

1. **Search for Songs**: Users can search for songs by name.
2. **Add to Queue**: Once the song is found, users can add it to the shared queue.
3. **Play Songs**: The music plays in the order it is added to the queue.
4. **Auto Play**: When one song ends, the next one in the queue starts automatically.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask), YouTube Music API, yt-dlp for audio streaming
- **Database**: In-memory queue (no persistent database)

## Installation

### Requirements

- Python 3.x
- Flask
- yt-dlp
- Flask-CORS

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Team-Music-Player.git
    cd Team-Music-Player
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask app:
    ```bash
    python server.py
    ```

4. Open your browser and go to `http://localhost:5000`.

## Usage

- **Main Page**: The main page is the queue where users can search for songs and add them to the queue. Team members can interact with the queue to add or remove songs, creating a collaborative music-playing experience.
- **Player Page**: The player page is where the song is actually playing. Users on this page can listen to the current song and control playback, while the queue is automatically updated in real time.

The queue is managed server-side, meaning songs will be played automatically in order, and team members can control the playlist without needing the person connected to the speaker to intervene.

