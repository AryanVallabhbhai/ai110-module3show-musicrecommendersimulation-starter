"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs   # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs     # python src/main.py


# Test profiles for stress-testing the recommender.
# First three are "realistic" listener types; last three are adversarial /
# edge cases meant to probe whether the scoring logic can be tricked.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    # --- adversarial / edge cases ---
    "Conflicting (loud but sad)": {"genre": "metal", "mood": "sad", "energy": 0.95},
    "Genre not in catalog": {"genre": "reggae", "mood": "chill", "energy": 0.5},
    "Empty preferences": {},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Run and pretty-print the top-k recommendations for one profile."""
    print(f"\n### Profile: {name}")
    print(f"prefs: {user_prefs}")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}  [score: {score:.2f}]")
        print(f"   because: {explanation}")
    print("-" * 60)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
