import time
import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Update Spotify 'My Library' playlist based on liked songs and albums."
)
parser.add_argument("--client_id", help="Spotify Client ID", required=True)
parser.add_argument("--client_secret", help="Spotify Client Secret", required=True)
args = parser.parse_args()

# Set up the Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
        redirect_uri="http://localhost/",
        scope="playlist-read-private user-library-read playlist-modify-public",
    )
)


def fetch_with_retry(func, *args, **kwargs):
    max_retries = 5
    backoff_factor = 0.5  # Delay factor that will be multiplied with the retry count
    retries = 0

    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(
                    e.headers.get("Retry-After", 1)
                )  # Default to 1 second if header is missing
                print(f"Rate limit hit, sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                print("Retrying request...")
            else:
                raise
        except ReadTimeout:
            wait = backoff_factor * (2**retries)
            print(f"Read timeout, sleeping for {wait:.1f} seconds...")
            time.sleep(wait)
            print("Retrying request...")
            retries += 1
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            wait = backoff_factor * (2**retries)
            time.sleep(wait)
            retries += 1

    raise Exception("Maximum retries reached")


def get_playlist_id(name):
    playlists = fetch_with_retry(sp.current_user_playlists)
    for playlist in playlists["items"]:
        if playlist["name"] == name:
            return playlist["id"]
    return None


def fetch_liked_songs():
    print("Fetching liked songs...")
    liked_songs = set()
    results = fetch_with_retry(sp.current_user_saved_tracks)
    liked_songs.update([item['track']['id'] for item in results['items']])
    print(f"Fetched {len(liked_songs)} liked songs so far...", end='\r')

    while results['next']:
        results = fetch_with_retry(sp.next, results)
        liked_songs.update([item['track']['id'] for item in results['items']])
        print(f"Fetched {len(liked_songs)} liked songs so far...", end='\r')
    
    return liked_songs

def fetch_album_tracks():
    print("Fetching tracks from liked albums...")
    album_tracks = set()
    album_results = fetch_with_retry(sp.current_user_saved_albums)

    while True:
        for album_item in album_results['items']:
            album_id = album_item['album']['id']
            track_results = fetch_with_retry(sp.album_tracks, album_id)
            
            while True:
                album_tracks.update([track['id'] for track in track_results['items']])
                print(f"Fetched {len(album_tracks)} tracks from liked albums so far...", end='\r')

                if track_results['next']:
                    track_results = fetch_with_retry(sp.next, track_results)
                else:
                    break

        if album_results['next']:
            album_results = fetch_with_retry(sp.next, album_results)
        else:
            break

    return album_tracks


playlist_name = "My Library"
playlist_id = get_playlist_id(playlist_name)

if not playlist_id:
    print(f"Creating playlist '{playlist_name}'...")
    playlist = fetch_with_retry(
        sp.user_playlist_create,
        sp.me()["id"],
        playlist_name,
        description="A playlist containing all my liked albums and tracks",
    )
    playlist_id = playlist["id"]
    print(f"Created playlist '{playlist_name}'")

# Fetch liked songs and album tracks
liked_track_ids = fetch_liked_songs()
album_track_ids = fetch_album_tracks()

# Combine liked songs and album tracks
all_track_ids = liked_track_ids.union(album_track_ids)

# Fetch current tracks in the playlist
print(f"Fetching existing tracks in '{playlist_name}'...")
playlist_tracks = set()
results = fetch_with_retry(sp.playlist_tracks, playlist_id)
playlist_tracks.update([item["track"]["id"] for item in results["items"]])
while results["next"]:
    results = fetch_with_retry(sp.next, results)
    playlist_tracks.update([item["track"]["id"] for item in results["items"]])

# Determine tracks to be added and removed
tracks_to_add = all_track_ids - playlist_tracks
tracks_to_remove = playlist_tracks - all_track_ids

# Limit the number of tracks to add to 10,000 due to Spotify's playlist limit
if len(tracks_to_add) > 10000:
    print(f"Limiting the number of tracks to add to 10,000 due to Spotify's playlist limit.")
    tracks_to_add = set(list(tracks_to_add)[:10000])

# Remove tracks no longer liked
tracks_to_remove = list(tracks_to_remove)
for i in range(0, len(tracks_to_remove), 100):
    fetch_with_retry(sp.playlist_remove_all_occurrences_of_items, playlist_id, tracks_to_remove[i:i + 100])
    print(f"Removed {min(i + 100, len(tracks_to_remove))}/{len(tracks_to_remove)} tracks from '{playlist_name}'", end='\r')
print(f"\nRemoved unliked tracks from '{playlist_name}'")

# Add new liked tracks (up to 10,000)
tracks_to_add = list(tracks_to_add)
for i in range(0, len(tracks_to_add), 100):
    fetch_with_retry(sp.playlist_add_items, playlist_id, tracks_to_add[i:i + 100])
    print(f"Added {min(i + 100, len(tracks_to_add))}/{len(tracks_to_add)} tracks to '{playlist_name}'", end='\r')
print(f"\nAdded new liked tracks to '{playlist_name}'")
