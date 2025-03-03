from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp
import os
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__, static_folder='static')
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

ytmusic = YTMusic()
queue = []  # Global queue for songs
stream_url_queue = []

def get_stream_url(video_id):
    """Get direct streaming URL for a song."""
    url = f"https://music.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "geo_bypass": True,
        "noplaylist": True,
        "extractaudio": True,
        "cookiefile": "/home/ubuntu/ytbot/cookie.txt",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get("url")
            return stream_url
    except Exception as e:
        print(f"Error fetching stream URL: {e}")
        return None

@app.route("/stream/<video_id>")
def stream(video_id):
    """Proxy the stream URL to the client."""
    global stream_url_queue

    # Find the song in the queue
    song = next((song for song in stream_url_queue if song["video_id"] == video_id), None)
    if not song or not song.get("real_stream_url"):
        return jsonify({"error": "Failed to get real stream URL"}), 500

    real_stream_url = song["real_stream_url"]

    # Stream the audio content to the client
    def generate():
        try:
            with requests.get(real_stream_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    yield chunk
        except requests.RequestException as e:
            print(f"Error streaming audio: {e}")
            return jsonify({"error": "Failed to stream audio"}), 500

    # Remove the song from stream_url_queue after streaming starts
    stream_url_queue = [s for s in stream_url_queue if s["video_id"] != video_id]

    return Response(stream_with_context(generate()), content_type="audio/mpeg")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    results = ytmusic.search(query, filter="songs")
    return jsonify(results)

@app.route("/queue", methods=["POST"])
def add_to_queue():
    data = request.json
    video_id = data.get("video_id")
    title = data.get("title")
    channel_name = data.get("channel_name")
    duration = data.get("duration")
    thumbnail_url = data.get("thumbnail_url")

    if not video_id:
        return jsonify({"error": "Invalid data"}), 400

    # Check if song is already in the queue
    if any(song["video_id"] == video_id for song in queue):
        return jsonify({"message": "Song already in queue"}), 200

    # Fetch the real stream URL
    real_stream_url = get_stream_url(video_id)
    stream_url_queue.append({"video_id": video_id,"real_stream_url": real_stream_url})
    if not real_stream_url:
        return jsonify({"error": "Failed to get real stream URL"}), 500
    # Add song to the queue with the server's stream URL and the real stream URL
    queue.append({
        "video_id": video_id,
        "title": title,
        "channel_name": channel_name,
        "thumbnail_url": thumbnail_url,
        "duration": duration,
        "stream_url": f"/stream/{video_id}",  # Server's stream URL
    })

    # Notify all clients about the updated queue
    socketio.emit("queue_updated", {"queue": queue})
    return jsonify({"message": "Added to queue"})

@app.route("/queue", methods=["GET"])
def get_queue():
    return jsonify(queue)

@app.route("/remove", methods=["POST"])
def remove_from_queue():
    global queue
    data = request.json
    video_id = data.get("video_id")
    if not video_id:
        return jsonify({"error": "Invalid data"}), 400

    queue = [song for song in queue if song["video_id"] != video_id]
    socketio.emit("queue_updated", {"queue": queue})  # Notify all clients
    return jsonify({"message": "Song removed from queue"})

@app.route("/play", methods=["GET"])
def play_next():
    global queue
    if not queue:
        return jsonify({"error": "Queue is empty"}), 400

    # Pop the first song from the queue
    song = queue.pop(0)
    socketio.emit("queue_updated", {"queue": queue})  # Notify all clients

    # Return the proxied stream URL (server's stream URL)
    return jsonify({
        "title": song["title"],
        "url": song["stream_url"]  # Use the proxy endpoint (server's stream URL)
    })

@app.route("/")
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

@app.route("/player")
def player():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'player.html')

@app.route("/styles.css")
def css():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'styles.css')

@app.route("/script.js")
def js():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'script.js')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
