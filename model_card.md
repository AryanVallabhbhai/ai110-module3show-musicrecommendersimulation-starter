# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

A small content-based music recommender that matches songs to a listener's stated "vibe."

---

## 2. Intended Use  

**Goal / task.** VibeFinder suggests songs that fit a user's taste. The user says what they
like — a genre, a mood, and how much energy they want — and the system returns a ranked list
of the best-matching songs, each with a short reason.

**Assumptions.** It assumes the user can describe their taste as a few simple values, and that
a song's "feel" is captured well enough by its genre, mood, and audio numbers (energy, valence,
danceability, acousticness, tempo).

**Intended use:** classroom exploration. It is a learning tool for understanding how
recommenders turn data into ranked suggestions.

**Not intended use:** it is not a real product. Do not use it to make decisions for real
listeners, to judge artists, or in any setting where a bad recommendation matters.

---

## 3. How the Model Works  

Think of it like a judge giving each song points. The user fills out a little taste card:
"I like pop, I want a happy mood, and give me high energy." The judge then looks at every
song in the catalog and adds up points:

- **+2 points** if the song's genre matches what the user asked for.
- **+1 point** if the song's mood matches.
- **Up to a few more points** for the number features (energy, valence, danceability,
  acousticness, tempo) — but here's the key: a song earns points for being *close* to the
  user's target, not for being high. So a user who wants calm music gets calm songs, not the
  loudest ones.

After every song has a total score, the system sorts them from highest to lowest and shows the
top few. That's the whole idea: score each song, then rank them.

**Changes from the starter.** The starter just returned the first few songs. I added the real
scoring rule, made it explain each pick with reasons, normalized tempo so fast songs don't
unfairly dominate, and grew the song list so there's more variety.

---

## 4. Data  

The catalog is a single CSV file with **18 songs** (I expanded it from the starter's 10).
Each song has: title, artist, genre, mood, and five audio numbers on a 0–1 scale (energy,
valence, danceability, acousticness) plus tempo in BPM.

**Genres:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, EDM, R&B,
classical, metal, country, and dream pop. **Moods:** happy, chill, intense, relaxed, moody,
focused, angry, energetic, sad, melancholic, romantic, and dreamy.

**Limits.** It's tiny. Many genres have only one or two songs, so a genre match is sometimes
the only option, not the best one. The data is also made-up, not from real listening. And it
misses big parts of taste: no lyrics, no language, no timbre/texture, and no sense of *why* or
*when* someone listens (workout, sleep, focus).

---

## 5. Strengths  

- It works well for **clear, single-minded users** — someone who wants "chill lofi" or
  "intense rock" gets exactly that. Opposite tastes are separated cleanly.
- The **closeness scoring** correctly captures the calm-vs-intense feel. Calm profiles get
  calm songs; high-energy profiles get high-energy songs. This matched my own intuition.
- Every recommendation comes with a **plain reason** ("genre match (+2.0); energy close to
  target"), so it's easy to see *why* a song ranked where it did.
- It **fails gracefully**: asking for a genre that isn't in the catalog just falls back to
  mood and energy instead of crashing.

---

## 6. Limitations and Bias 

**Genre dominance / conflicting-signal bias.** The biggest weakness I found during
stress-testing is that genre (+2.0) can outweigh a *wrong* mood entirely. My adversarial
"loud but sad" profile (`genre=metal, mood=sad, energy=0.95`) returned Iron Verdict — a
loud, dark metal track — as #1 purely on genre + energy, even though its mood is nothing
like "sad." The one genuinely sad song (Letters Unsent) fell to #2 because its low energy
lost points on the energy gap. So a user with mixed feelings gets served the genre label,
not the emotional tone they asked for.

**Redundant "calmness" stacking.** Because energy, tempo, and acousticness all move together
for mellow music, calm profiles effectively get their preference counted ~3x, which
over-penalizes energetic genres and can create a mild filter bubble for chill listeners.

**No tie-breaking and thin data.** With empty preferences every song scores 0.00 and the
system just returns CSV order — meaningless. The catalog is also only 18 songs, so several
genres (rock, metal, country) have just one representative, meaning a genre match is
sometimes the *only possible* match, not the *best* one.

---

## 7. Evaluation  

I stress-tested six profiles: three realistic listeners (**High-Energy Pop**, **Chill Lofi**,
**Deep Intense Rock**) and three adversarial edge cases (**Conflicting: loud but sad**,
**Genre not in catalog: reggae**, **Empty preferences**). For each I ran
`python -m src.main` and inspected the top 5. I was checking two things: (1) does the
top pick match the profile's intent, and (2) do the edge cases fail gracefully.

**Profile comparisons:**

- **High-Energy Pop vs Chill Lofi** — Pop pulls bright, fast tracks (Sunrise City, Gym Hero);
  Lofi shifts to slow, acoustic, low-energy tracks (Library Rain, Midnight Coding). Opposite
  ends of the energy axis, exactly as expected.
- **Chill Lofi vs Deep Intense Rock** — near mirror images: Lofi tops out around energy 0.35
  with acoustic songs, Rock tops out near 0.9 with loud ones. This confirms the profile can
  cleanly separate opposites.
- **Deep Intense Rock vs Conflicting (loud but sad)** — both surface loud songs, but the
  conflicting profile's genre (metal) wins over its mood (sad), so it returns aggressive metal
  instead of anything actually sad — showing genre outranks mood when they disagree.
- **Chill Lofi vs Genre-not-in-catalog (reggae)** — with no reggae in the data, the reggae
  profile can't earn genre points, so it degrades to a mood+energy match and returns chill
  tracks — same *feel* as Lofi but without the confident genre boost.

**What surprised me:** in the "loud but sad" test I expected mood to matter more; instead the
recommender confidently returned metal, which taught me my genre weight is doing most of the
work. The **Empty preferences** case also surprised me — every song scored 0.00 and the output
became arbitrary CSV order, revealing a missing tie-break.

**Weight experiment.** I doubled energy (1.5 → 3.0) and halved genre (2.0 → 1.0). Storm Runner
(rock) jumped into the top 5 of the High-Energy Pop list, because a strong energy match now
beats a genre match. The result was *more diverse* and arguably more faithful to a user who
truly prioritizes energy — a useful lever for trading genre loyalty against cross-genre
discovery. (Full before/after output is in the README **Experiments You Tried** section.)

---

## 8. Future Work  

If I kept building VibeFinder, I would:

1. **Fix the genre-vs-mood imbalance.** Let genre be a soft "similar genres" match instead of
   exact-only, and give mood more say so a "sad" request isn't buried by a genre match.
2. **Add a tie-break and a bigger catalog.** A secondary sort (e.g. by title) would stop the
   empty-preference case from returning arbitrary order, and more songs per genre would give
   real variety instead of one-of-a-kind matches.
3. **Support ranges and context.** Let users say "energy between 0.3 and 0.5" instead of one
   exact number, and add context like activity (workout, study, sleep) — that's closer to how
   people actually pick music.

---

## 9. Personal Reflection  

**Biggest learning moment.** Seeing that a recommendation is really just *score every item,
then sort*. Once I built the scoring rule, "recommending" was almost free — it's ranking. That
demystified how big apps work: the magic is in the features and weights, not some secret sauce.

**How AI tools helped, and when I double-checked.** The AI assistant was fast at scaffolding —
writing the CSV loader, the scoring loop, and clean terminal output. But I had to double-check
the *weights* and the *math*. It was easy to accidentally reward "high energy" instead of
"close to target energy," and only testing with real profiles caught whether the logic actually
matched intent. The adversarial profiles (like "loud but sad") were where I learned the most,
because they exposed that my genre weight was quietly running the whole show.

**What surprised me.** How much a handful of numbers and two `if` statements can *feel* like a
real recommendation. There's no machine learning here — just weighted addition — yet the output
reads like the app "gets" the vibe. It made me realize a lot of "smart" features are simpler
than they look, and also that simple rules carry hidden biases you don't see until you probe them.

**What I'd try next.** I'd add collaborative filtering — using what similar users liked — so the
system could surprise me with cross-genre picks instead of only returning more of what I already
asked for. That's the piece a pure content-based system can't do on its own.
