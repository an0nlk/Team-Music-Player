let isPlaying = false;
let queue = [];

//escape chars
function htmlEscape(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// Search for songs
async function search() {
    const query = document.getElementById("query").value;
    if (!query) return;

    document.getElementById("search-loading").style.display = 'block';
    try {
        const res = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        document.getElementById("search-results").getElementsByTagName('tbody')[0].innerHTML = data.map(song => 
            `<tr>
                <td><img src="${song.thumbnails[0].url}" alt="Thumbnail"></td>
                <td>${song.title}</td>
                <td>${song.artists[0].name}</td>
                <td>${song.duration}</td>
                <td>
                    <button onclick="addToQueue('${htmlEscape(song.videoId)}', '${htmlEscape(song.title)}', '${htmlEscape(song.artists[0].name)}', '${htmlEscape(song.duration)}', '${htmlEscape(song.thumbnails[0].url)}')">
						Add
					</button>

                </td>
            </tr>`).join("");
    } catch (error) {
        console.error("Search error:", error);
        alert("Failed to fetch search results.");
    } finally {
        document.getElementById("search-loading").style.display = 'none';
    }
}

// Add a song to the queue
async function addToQueue(video_id, title, channel_name, duration, thumbnail_url) {
    // Locate the add button (using a more generic selector; consider passing the button element to avoid fragility)
    const addButton = document.querySelector(`button[onclick*="addToQueue('${video_id}'"]`);
    if (addButton) {
        addButton.innerHTML = 'Adding...';
        addButton.disabled = true;
    }
    
    try {
        await fetch("/queue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video_id, title, channel_name, duration, thumbnail_url }),
        });
        updateQueue();
    } catch (error) {
        console.error("Add to queue error:", error);
        alert("Failed to add song to queue.");
    } finally {
        if (addButton) {
            addButton.innerHTML = 'Add';
            addButton.disabled = false;
        }
    }
}

// Update the queue display (removed auto-play on update)
async function updateQueue() {
    try {
        const res = await fetch("/queue");
        const data = await res.json();
        queue = data;
        document.getElementById("queue").getElementsByTagName('tbody')[0].innerHTML = data.map(song => 
            `<tr>
                <td><img src="${song.thumbnail_url}" alt="Thumbnail"></td>
                <td>${song.title}</td>
                <td>${song.channel_name}</td>
                <td>${song.duration}</td>
                <td><button onclick="removeFromQueue('${song.video_id}')">Remove</button></td>
            </tr>`).join("");
    } catch (error) {
        console.error("Queue update error:", error);
    }
}

// Remove a song from the queue
async function removeFromQueue(videoId) {
    try {
        await fetch("/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video_id: videoId }),
        });
        updateQueue();
    } catch (error) {
        console.error("Remove from queue error:", error);
    }
}

// Play the next song by calling the server's /play endpoint
async function playNext() {
    try {
        const res = await fetch('/play');
        const data = await res.json();

        if (data.error) {
            console.log(data.error);
            // Update the "nowPlaying" element to show the error message
            document.getElementById("nowPlaying").innerText = data.error;
            return;
        }

        const audio = document.getElementById("audioPlayer");
        audio.src = data.url;
        await audio.play();  // Await play() in case it returns a promise
        document.getElementById("nowPlaying").innerText = `🎵 ${data.title}`;
        isPlaying = true;
    } catch (error) {
        console.error("Error playing next song:", error);
    }
}


// When a song ends, reset the playing flag and play the next song
function onSongEnded() {
    isPlaying = false;
    playNext();
}

// Toggle play/pause for the audio player
async function togglePlayPause() {
    const audio = document.getElementById("audioPlayer");

    // If no song is loaded (audio.src is empty), load the next song.
    if (!audio.src) {
        // Attempt to load and play the next song.
        await playNext();
        // Exit the function; playNext() already starts playback if successful.
        return;
    }

    // If a song is loaded, toggle its play/pause state.
    if (audio.paused) {
        await audio.play();  // Await in case play() returns a promise
        document.getElementById("playPauseButton").innerText = "Pause";
    } else {
        audio.pause();
        document.getElementById("playPauseButton").innerText = "Play";
    }
}


// Initialize the queue when the page loads
window.onload = function() {
    updateQueue();
};

// Initialize WebSocket connection for real-time updates
const socket = io();
socket.on('queue_updated', function(data) {
    queue = data.queue;
    updateQueue();
});
