import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Scoring weights (Algorithm Recipe, Phase 2) ---
W_GENRE = 2.0
W_MOOD = 1.0
W_ENERGY = 1.5
W_VALENCE = 1.5
W_DANCEABILITY = 1.0
W_ACOUSTICNESS = 1.0

# Tempo min/max used to normalize BPM to 0-1 before scoring.
# Bounds cover the catalog with headroom so out-of-range values clamp cleanly.
TEMPO_MIN = 50.0
TEMPO_MAX = 180.0

# Columns that must be numeric after CSV load.
FLOAT_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _closeness(value: float, target: float) -> float:
    """Reward nearness, not magnitude: 1.0 = exact match, 0.0 = opposite.

    Both inputs must be on the same 0-1 scale.
    """
    return 1.0 - abs(value - target)


def _norm_tempo(bpm: float) -> float:
    """Min-max scale a BPM into 0-1, clamped to [0, 1]."""
    scaled = (bpm - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)
    return max(0.0, min(1.0, scaled))


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one Song against a UserProfile. Returns (score, reasons)."""
        score = 0.0
        reasons: List[str] = []

        if song.genre == user.favorite_genre:
            score += W_GENRE
            reasons.append(f"genre match ({song.genre}, +{W_GENRE})")

        if song.mood == user.favorite_mood:
            score += W_MOOD
            reasons.append(f"mood match ({song.mood}, +{W_MOOD})")

        energy_pts = W_ENERGY * _closeness(song.energy, user.target_energy)
        score += energy_pts
        reasons.append(f"energy close to target (+{energy_pts:.2f})")

        # UserProfile carries only a boolean acoustic preference, so map it to
        # a target of 1.0 (likes acoustic) or 0.0 (does not) and reward closeness.
        acoustic_target = 1.0 if user.likes_acoustic else 0.0
        acoustic_pts = W_ACOUSTICNESS * _closeness(song.acousticness, acoustic_target)
        score += acoustic_pts
        reasons.append(f"acousticness fit (+{acoustic_pts:.2f})")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Scoring rule: score every song. Ranking rule: sort desc, take top-k.
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = self._score(user, song)
        return f"score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dicts.
    Numeric fields are converted to float so they can be scored later.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song (dict) against user preferences (dict).
    Implements the Algorithm Recipe from Phase 2.

    user_prefs keys (all optional except where you want a signal):
        genre, mood, energy, valence, danceability, acousticness, tempo_bpm
    Returns (score, reasons).
    """
    score = 0.0
    reasons: List[str] = []

    if "genre" in user_prefs and song["genre"] == user_prefs["genre"]:
        score += W_GENRE
        reasons.append(f"genre match ({song['genre']}, +{W_GENRE})")

    if "mood" in user_prefs and song["mood"] == user_prefs["mood"]:
        score += W_MOOD
        reasons.append(f"mood match ({song['mood']}, +{W_MOOD})")

    # Numeric features: reward closeness to target, scaled by weight.
    numeric = (
        ("energy", "energy", W_ENERGY, False),
        ("valence", "valence", W_VALENCE, False),
        ("danceability", "danceability", W_DANCEABILITY, False),
        ("acousticness", "acousticness", W_ACOUSTICNESS, False),
        ("tempo_bpm", "tempo_bpm", 1.0, True),
    )
    for pref_key, song_key, weight, is_tempo in numeric:
        if pref_key not in user_prefs:
            continue
        if is_tempo:
            song_val = _norm_tempo(song[song_key])
            target = _norm_tempo(user_prefs[pref_key])
        else:
            song_val = song[song_key]
            target = user_prefs[pref_key]
        pts = weight * _closeness(song_val, target)
        score += pts
        reasons.append(f"{pref_key} close to target (+{pts:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional recommendation: score each song, rank, return top-k.
    Returns list of (song_dict, score, explanation).
    Required by src/main.py
    """
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no matching preferences"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
