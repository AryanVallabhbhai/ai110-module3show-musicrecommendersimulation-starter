# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders (Spotify, YouTube) predict what you'll love next by mixing two ideas: collaborative filtering (people with similar behavior liked X, so you might too)
and content-based filtering (this song's own attributes — tempo, energy, mood — resemble songs you already like). They learn from explicit signals (likes, saves, follows) and, more
heavily, implicit signals (skips, play-completion, replays, session context). Big platforms run hybrids of both to balance surprise against relevance.

My version is a pure content-based recommender. It ignores other users entirely and scores songs only by how close their attributes are to a user's stated taste profile. I prioritize match, not magnitude — a song scores high because its energy/valence/etc. sit near the user's preference, not because those values are large. Genre is weighted highest (a hard identity constraint), energy and valence next (the core "vibe" axes), and mood lowest because in this dataset mood is largely redundant with energy + valence.

Scoring rule (one song): for each numeric feature, `feat_score = 1 - abs(song - user_pref)`
(1 = perfect match, 0 = opposite). Categoricals score 1 on exact match, else 0. Final score is a weighted sum. Ranking rule (many songs): score every song, sort descending, return top-N.
Both steps are needed — scoring produces a comparable number per song; ranking turns that pile of numbers into an ordered recommendation list.

### Algorithm Recipe (finalized)

```
score(song, user) =
      +2.0                                                   if song.genre == user.favorite_genre
    + +1.0                                                   if song.mood  == user.favorite_mood
    + 1.5 * (1 - |song.energy       - user.target_energy|)
    + 1.5 * (1 - |song.valence      - user.target_valence|)
    + 1.0 * (1 - |song.danceability - user.target_danceability|)
    + 1.0 * (1 - |song.acousticness - user.target_acousticness|)
    + 1.0 * (1 - |tempo_norm        - user.target_tempo_norm|)   # tempo min-max scaled to 0-1
```

- Genre match = flat **+2.0** (strongest signal, defines identity).
- Mood match = flat **+1.0** (weaker; partly redundant with energy + valence).
- Numeric features = **graded** by closeness, not magnitude — a song scores high for being
  *near* the target, never just for being large. Max possible score ≈ 9.0.

### Data Flow

```text
INPUT                    PROCESS (the loop)           OUTPUT
UserProfile  ─┐
              ├─►  for each song in CSV:        ─►  sort by score desc  ─►  Top-K recs
songs.csv  ───┘        score(song, user)
```

### Potential Biases

- **Genre over-prioritization.** At +2.0, genre can outrank several close numeric matches
  combined. A lofi-perfect *ambient* song is rejected purely for its label, even though it
  sounds closer to the user's taste than some lofi tracks. Exact-match genre is brittle.
- **Redundancy stacking.** For calm listeners, low energy + low tempo + high acousticness all
  move together, so "calmness" gets weighted ~3× unintentionally — inflating confidence and
  over-punishing energetic genres.
- **Point-target rigidity.** A single target value per feature models no *range* of taste, so
  the system separates opposites (rock vs lofi) cleanly but handles mid-vibe songs poorly.
- **Popularity/discovery blind spot.** Pure content-based → no surprise, no cross-genre finds
  (that's what collaborative filtering adds in real systems).

### Features used

- **`Song`**: `genre`, `mood` (categorical); `energy`, `valence`, `danceability`,
  `acousticness` (numeric 0–1); `tempo_bpm` (min-max normalized to 0–1 before scoring).
- **`UserProfile`**: a preferred value for each of the above (e.g. `pref_energy=0.4`,
  `pref_genre="lofi"`, `pref_mood="chill"`), plus per-feature **weights**
  (`w_genre=2.0`, `w_energy=1.5`, `w_valence=1.5`, `w_danceability=1.0`,
  `w_acousticness=1.0`, `w_mood=0.5`).
- **`Recommender`**: applies the scoring rule to each `Song` against the `UserProfile`, then
  the ranking rule to return the top-N.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default **pop / happy / energy=0.8** profile:

```text
Loaded songs: 18

User profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}

Top recommendations:
============================================================
1. Sunrise City - Neon Echo  [score: 4.47]
   because: genre match (pop, +2.0); mood match (happy, +1.0); energy close to target (+1.47)
2. Gym Hero - Max Pulse  [score: 3.30]
   because: genre match (pop, +2.0); energy close to target (+1.30)
3. Rooftop Lights - Indigo Parade  [score: 2.44]
   because: mood match (happy, +1.0); energy close to target (+1.44)
4. Concrete Verses - Blockprint  [score: 1.43]
   because: energy close to target (+1.43)
5. Night Drive Loop - Neon Echo  [score: 1.42]
   because: energy close to target (+1.42)
============================================================
```

The top pick (Sunrise City) hits genre **and** mood **and** near-target energy, exactly as the
recipe intends. Pure energy matches (rows 4-5) still surface but rank below any genre/mood hit.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Stress test — six profiles

Ran `python -m src.main`, which scores three realistic profiles and three adversarial
edge cases. Top 5 for each:

```text
### Profile: High-Energy Pop
prefs: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9}
------------------------------------------------------------
1. Sunrise City - Neon Echo  [score: 4.38]  genre+mood+energy
2. Gym Hero - Max Pulse  [score: 3.46]  genre+energy
3. Rooftop Lights - Indigo Parade  [score: 2.29]  mood+energy
4. Storm Runner - Voltline  [score: 1.48]  energy only
5. Concrete Verses - Blockprint  [score: 1.42]  energy only

### Profile: Chill Lofi
prefs: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}
------------------------------------------------------------
1. Library Rain - Paper Lanterns  [score: 4.50]  genre+mood+energy
2. Midnight Coding - LoRoom  [score: 4.39]  genre+mood+energy
3. Focus Flow - LoRoom  [score: 3.42]  genre+energy
4. Spacewalk Thoughts - Orbit Bloom  [score: 2.40]  mood+energy
5. Coffee Shop Stories - Slow Stereo  [score: 1.47]  energy only

### Profile: Deep Intense Rock
prefs: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}
------------------------------------------------------------
1. Storm Runner - Voltline  [score: 4.48]  genre+mood+energy
2. Gym Hero - Max Pulse  [score: 2.46]  mood+energy
3. Iron Verdict - Blackspire  [score: 2.38]  mood+energy
4. Concrete Verses - Blockprint  [score: 1.42]  energy only
5. Warehouse Pulse - Kilohertz  [score: 1.41]  energy only

### Profile: Conflicting (loud but sad)  [adversarial]
prefs: {'genre': 'metal', 'mood': 'sad', 'energy': 0.95}
------------------------------------------------------------
1. Iron Verdict - Blackspire  [score: 3.46]  genre+energy (mood 'sad' ignored!)
2. Letters Unsent - Grey Harbor  [score: 1.57]  mood+energy
3. Warehouse Pulse - Kilohertz  [score: 1.48]  energy only
4. Gym Hero - Max Pulse  [score: 1.47]  energy only
5. Storm Runner - Voltline  [score: 1.44]  energy only

### Profile: Genre not in catalog (reggae)  [adversarial]
prefs: {'genre': 'reggae', 'mood': 'chill', 'energy': 0.5}
------------------------------------------------------------
1. Midnight Coding - LoRoom  [score: 2.38]  mood+energy (no genre possible)
2. Library Rain - Paper Lanterns  [score: 2.27]  mood+energy
3. Spacewalk Thoughts - Orbit Bloom  [score: 2.17]  mood+energy
4. Dust Road Home - Cody Wren  [score: 1.47]  energy only
5. Cloud Ferry - Halcyon Kite  [score: 1.47]  energy only

### Profile: Empty preferences  [adversarial]
prefs: {}
------------------------------------------------------------
1-5. all score 0.00 -> returns CSV order (no tie-break)
```

**Findings:** genre match dominates conflicting signals (metal beats "sad"); missing genre
degrades gracefully to mood+energy; empty prefs exposes a missing tie-break.

### Weight experiment — double energy, halve genre

Changed `W_ENERGY` 1.5 → 3.0 and `W_GENRE` 2.0 → 1.0, re-ran High-Energy Pop:

```text
EXPERIMENT: W_ENERGY 1.5->3.0, W_GENRE 2.0->1.0
Profile: High-Energy Pop {'genre': 'pop', 'mood': 'happy', 'energy': 0.9}
------------------------------------------------------------
1. Sunrise City - Neon Echo  [score: 4.76]  genre(+1.0)+mood+energy(+2.76)
2. Gym Hero - Max Pulse  [score: 3.91]  genre+energy(+2.91)
3. Rooftop Lights - Indigo Parade  [score: 3.58]  mood+energy(+2.58)
4. Storm Runner - Voltline  [score: 2.97]  energy only(+2.97)  <-- rock, now competitive
5. Concrete Verses - Blockprint  [score: 2.85]  energy only
```

**Result:** more *diverse*, not just different. Storm Runner (rock) climbs because a strong
energy match now beats a genre match — better for a user who genuinely prioritizes energy over
genre loyalty. Trade-off lever between relevance-to-genre and cross-genre discovery.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



