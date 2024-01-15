# Spotify Library Playlist Create/Update Script

## Description
Since Spotify has not yet implemented the ability to shuffle both your liked songs and songs from liked albums in one large "Library" shuffle, I developed this script. This script updates a specific Spotify playlist ("My Library") based on the user's liked songs and tracks from liked albums. It ensures that the playlist reflects the current state of the user's likes, adding new tracks and removing those that are no longer liked.

## Requirements
- Python 3.x
- Spotipy (A lightweight Python library for the Spotify Web API)

To install Spotipy, run:
```bash
pip install spotipy
```

## Spotify Developer Account Setup
To use this script, you need to set up a Spotify Developer account and create an application. Follow these steps:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in with your Spotify account, or create one if you don't already have it.
3. Once logged in, create a new application. This will provide you with the `Client ID` and `Client Secret` required by the script.
4. In your application settings, add a Redirect URI. This script uses `http://localhost/` by default.
5. Note down your `Client ID` and `Client Secret` for use with the script.

## Authentication Process
When you run the script for the first time, it will open a web browser window for Spotify authentication. Follow these steps:

1. A web page will ask you to log in to your Spotify account (if not already logged in) and authorize the application to access your data.
2. After authorization, Spotify will redirect you to another web page (as set in the Redirect URI, default is `http://localhost/`).
3. Copy the URL of this web page from your browser's address bar.
4. Paste this URL back into the terminal where the script is running.

This process is required only once; the script will remember your credentials for future executions.

## Command Line Arguments
The script accepts two mandatory arguments:
- `--client_id`: Your Spotify Application's Client ID.
- `--client_secret`: Your Spotify Application's Client Secret.

### Usage
Run the script from the command line, providing the necessary arguments. For example:
```bash
python spotify-mylibrary.py --client_id YOUR_SPOTIFY_CLIENT_ID --client_secret YOUR_SPOTIFY_CLIENT_SECRET
```
Replace `YOUR_SPOTIFY_CLIENT_ID` and `YOUR_SPOTIFY_CLIENT_SECRET` with your actual Spotify Developer application credentials.
