from dotenv import load_dotenv
import os
import spotipy
import json
import cv2
from spotipy.oauth2 import SpotifyOAuth
from deepface import DeepFace
from flask import Flask, session, redirect, request, url_for, render_template



load_dotenv()   # reads .env into os.environ

CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SECRET_KEY    = os.getenv("SECRET_KEY")


app = Flask(__name__)
app.config.update(
    SECRET_KEY = SECRET_KEY,
    TESTING = True
)


def get_authorized(scope = None):
    """ 
    Get authorization for Spotify API optional scope 
    argument that is not necessary for requests
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope)) 
    return sp


def get_emotion(img_path):
    """
    Uses Deepface ML to get the emotions from the image
    that was uploaded
    """
    data_string = DeepFace.analyze(img_path, "emotion")
    data_json =json.loads(data_string)
    return data_json


@app.route("/detect_and_play", methods =['POST'])
def detect_and_play():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("Image processing Error")
        return
    emotions = get_emotion(frame)
    
    
