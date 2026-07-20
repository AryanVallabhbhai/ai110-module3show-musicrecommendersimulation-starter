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


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    print(f"\nUser profile: {user_prefs}")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}  [score: {score:.2f}]")
        print(f"   because: {explanation}")
    print("=" * 60)


if __name__ == "__main__":
    main()
