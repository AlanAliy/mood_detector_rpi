from dotenv import load_dotenv
import os
import spotipy
import json
import cv2
from spotipy.oauth2 import SpotifyOAuth
from deepface import DeepFace
from flask import Flask, session, redirect, request, url_for, render_template



load_dotenv()   # reads .env into os.environ
print("SPOTIPY_REDIRECT_URI:", os.getenv("SPOTIPY_REDIRECT_URI"))

CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SECRET_KEY    = os.getenv("SECRET_KEY")

EMOTION_PLAYLISTS = {
    "angry": "spotify:playlist:37i9dQZF1EIgNZCaOGb0Mi",
    "disgust": "spotify:playlist:37i9dQZF1E8KEaf5o7wGZB",
    "fear": "spotify:playlist:5A16Qc2yGTZnVPJGuWBYBN",
    "happy": "spotify:playlist:37i9dQZF1EIgG2NEOhqsD7",
    "sad": "spotify:playlist:37i9dQZF1EIg6gLNLe52Bd",
    "surprise": "spotify:playlist:37i9dQZF1E8P9e4WhpIhrd",   
    "neutral":  "spotify:playlist:4ADcSA8oePEucvwIOv5lzj"

}


app = Flask(__name__)
app.config.update(
    SECRET_KEY = SECRET_KEY,
    TESTING = True
)



def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-playback-state user-modify-playback-state streaming user-read-currently-playing",
        cache_path=None,  # No caching so each user logs in
        show_dialog=True
    )

def get_authorized(scope=None):
    sp_oauth = get_spotify_oauth()
    token_info = session.get("token_info", None)

    if not token_info:
        return redirect(url_for("login"))

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    print("✅ Granted scopes:", token_info.get("scope"))
    return spotipy.Spotify(auth=token_info["access_token"])


   
def preprocess_image(frame):
    img = cv2.resize(frame, (800, 800))  # safe working size
    return img

def get_emotion(img_path):
    img = preprocess_image(img_path)
    result = DeepFace.analyze(img, detector_backend="ssd", actions=["emotion"], enforce_detection=False)
    if isinstance(result, list):
        result = result[0]  # take the first detected face
    return result["dominant_emotion"]


def play_4_emotion(sp, emotion):
    playlist_uri = EMOTION_PLAYLISTS.get(emotion)
    devices = sp.devices()
    if not devices["devices"]:
        print("No Spotify devices found")
        print("DEVICES:")
        print(json.dumps(devices, indent=2))
        return
    print("DEVICES:")
    print(json.dumps(devices, indent=2))

    device_id = devices["devices"][0]["id"]
    sp.start_playback(device_id=device_id, context_uri=playlist_uri)


@app.route("/login")
def login():
    session.clear()  # this is critical
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    
    return redirect(auth_url)

@app.route("/callback")
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session["token_info"] = token_info
    return redirect(url_for("detect_and_play"))


@app.route("/detect_and_play", methods =['POST', 'GET'])
def detect_and_play():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
   
    if not ret:
        return "Image Processing Error", 500 #internal server error
   
    processed = preprocess_image(frame)
    emotion = get_emotion(processed)
    
    sp = get_authorized(scope="user-read-playback-state user-modify-playback-state")
    play_4_emotion(sp, emotion)

    return f"Detected emotion: {emotion}. Playing corresponding Spotify playlist.", 200




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True)