# RUNBOOK – daily reel run

Owner: Lukas. Goal: 2 animated English educational Shorts per day (topics vary freely) on **YouTube Shorts + TikTok**, improved every day from the analytics.
One daily run (started by a scheduled task, ~17:40 Berlin) does everything below. Write all messages to Lukas in **German**, short and direct.

## 0 · Setup (fresh session)
1. Attach + clone this repo: `add_repo lukaspm2008-crypto/reels` (access: push), then
   `git clone --depth 1 https://github.com/lukaspm2008-crypto/reels /home/claude/reels`.
2. `bash /home/claude/reels/setup.sh` (installs skia-python, kokoro-onnx …, downloads the voice model to /tmp/kokoro).
3. Read `state/channel_memory.md` and `state/video_log.md`.

## 1 · Analytics → Keep/Kill/Test  (model: **Haiku**)
Spawn an Agent with `model: "haiku"` (general-purpose). Give it: the video_log table, the benchmarks below, and the task:
- Open (Claude in Chrome, new tab) **YouTube Studio → Inhalte → Shorts** and **TikTok Studio → Beiträge / Analyse** and read, for every
  video published in the last 7 days: views, avg % viewed / avg watch time, likes, comments, shares, saves (TikTok), and the
  retention curve / swipe-away rate if shown (note the second where the biggest drop happens).
- Fill the numbers into `state/video_log.md`.
- Evaluate against benchmarks and return a short verdict: best + worst video and **why** (hook, topic, pacing, drop-off second),
  and 1–3 concrete changes for today's videos. Never guess numbers; mark missing data as missing.
If the subagent cannot use the Chrome tools, collect the raw numbers yourself in Chrome and pass them to the Haiku agent only for the evaluation.

Benchmarks: 3 s hold < 60 % critical (rebuild hook) · 60–72 % solid · > 72 % strong.
Avg % viewed < 45 % mid-video drop (more visual changes, open loop by second 12) · 45–65 % good · > 65 % strong.
Shares/views < 1.5 % weak · saves/views < 2 % weak · comments/views < 0.5 % weak.

Then update `state/channel_memory.md` (move proven rules to KEEP/KILL, add/close TEST hypotheses). Each change must cite the numbers.
Videos younger than 24 h: don't judge them yet.

## 2 · Produce 2 videos  (model: **Opus**)
For each of the two videos spawn an Agent with `model: "opus"` and this brief: today's Keep/Kill/Test rules + the topic + "follow RUNBOOK section 2".
Run the two agents one after the other (they share the CPU).

### 2a Topic + script
- Pick a topic from any category (backlog in channel_memory or your own idea) – vary categories, never repeat a topic from video_log,
  and give the two daily videos different categories unless the analytics clearly favour one.
- Verify the core fact with WebSearch; note the source (author, year). If the fact is shaky, pick another topic.
- Write 12 lines (one per scene), 105–125 words total, hook ≤ 13 words, open loop in line 2–3, payoff at the end, and a
  last line that flows grammatically back into line 1 (seamless loop). Short, spoken, no filler ("In this video…").

### 2b Episode code
- `cp -r episodes/001-spotlight-effect episodes/<NNN>-<slug>`; delete its `build/`; edit `episode.py`:
  META (id, topic, source, youtube_title ≤ 70 chars incl. "#shorts", youtube_description, tiktok_caption, both with 4 hashtags and a
  "Send this to someone who…" line), LINES, CAPS (2–4 words per block, `*word*` = yellow highlight), TAIL, **remove DESIGN_DUR**,
  write 12 new scene functions `sN(c, t, D)` (t = seconds into the scene, D = scene length) and `SCENES`, and `sfx_cues`.
- Reuse `engine/lib.py`: `mika()`, `person()`, `bust()`, `head()`, `beam()`, `room()`/`GRID`, `stage()`, `classroom_bg()`,
  `classmates_desks()`, `ost()` (top headline, max 3–4 words), easing `eout/eback/einout/ebounce`, `cam()` for zooms.
  Add new props as functions inside the episode (or in lib.py if reusable).
- Rules: a new visual impulse every ≤ 3.5 s (zoom, pop, cut, counter…), something moving in frame 0 (no static first frame),
  numbers shown on screen, lower third (y > 1380) kept free except captions, last scene ends on the exact first frame of scene 1
  (see 001's `s12` crossfade) so the loop is seamless. No real people, brands, logos or copyrighted characters.
- **Quality bar – "Liebe im Detail" (Lukas, 2026-11-27: videos must look more premium, more love in the details).** Every scene must pass:
  1. *Full frame*: no big empty areas. The subject fills the upper 2/3 (y 180–1380); floors/walls carry detail (skirting board, tiles,
     posters, plants, shelf, rug, cables, light patches). Below the caption pill: ground/props continue, never a flat empty strip.
  2. *Depth*: soft contact shadow under every figure/object, 2-tone shading on big shapes (lighter top, darker side/bottom), subtle
     background gradient + vignette, foreground element out of focus or overlapping now and then (parallax layer that moves faster).
  3. *Life*: characters never freeze – blink every 2–4 s, breathing bob, hair/hoodie-string sway, eyes follow the action; ambient motion
     in every scene (dust motes, steam, flicker, clock hand, swaying lamp, drifting clouds).
  4. *Transitions*: no plain hard cuts between scenes – use match cuts, whip pans with motion blur, zoom-throughs or wipes in the
     palette colours (≈ 0.25 s). Pops use squash & stretch + small overshoot; counters tick with a tick SFX.
  5. *Typography*: headline plate with drop shadow, words pop in one by one; numbers count up; key numbers get a little sticker/badge.
  6. *Sound*: every visual event has an SFX (whoosh on transitions, pop, tick, ding, paper, footsteps); room tone/ambience fitting the
     scene (cafeteria murmur, birds, hum) under the voice; music ducked under VO.
  7. *Polish pass*: before the full build look at ≥ 8 test frames at full size and list for each one thing that could be nicer – fix
     the top 5. Charts/infographics are illustrated objects (paper card, whiteboard, phone screen), never bare shapes on cream.
- Check frames before the full build: `python3 engine/run.py episodes/<id> test 1@0.5 1@2.5 5@1 9@2 12@2` and look at the PNGs
  in `build/` (Read tool). Fix overlaps/cut-off text.
- Build: `python3 engine/run.py episodes/<id>` → `build/final.mp4`, `build/upload.mp4` (< 3.6 MB for browser upload), `build/contact.png`.
- Look at `contact.png`. Fix anything broken and rebuild once.

## 3 · Upload (Claude in Chrome, Lukas' logged-in Chrome)
Load the chrome-browser skill first. Use **build/upload.mp4**. Slot A → publish **08:00 Berlin tomorrow**, slot B → **23:00 Berlin today**
(if 23:00 already passed: publish B immediately). Use each platform's own scheduler so Lukas' PC needn't be on at publish time.
- **YouTube Studio** (studio.youtube.com): upload icon top right → `find` the hidden file-input → `file_upload` → title field (ctrl+a, type
  youtube_title) → description → "Nein, es ist nicht speziell für Kinder" → Weiter ×3 → Sichtbarkeit: **Planen** (date + time) or
  Öffentlich → Planen/Veröffentlichen. Copy the Shorts link into video_log.
- **TikTok Studio** (tiktok.com/tiktokstudio/upload): `find` the hidden file-input → `file_upload` → description (ctrl+a, type
  tiktok_caption; click outside to close hashtag suggestions) → "Wann veröffentlichen": **Zeitplan** (date + time) → Planen/Veröffentlichen.
  If a "veröffentlichen, bevor die Prüfung abgeschlossen ist?" dialog appears, confirm.
- If Chrome is not reachable: still build + commit both episodes, mark them `pending upload` in video_log; the next run uploads them first.
- Never claim an upload happened without seeing the platform's confirmation.

## 4 · Commit + report
- Add rows to `state/video_log.md` (id, topic, hook type, scheduled time, links/status).
- `git add -A && git commit -m "Run <date>: <ids>" && git -c push.negotiate=true push`.
- Send Lukas one short German message: what was analysed (1–2 key numbers + the change), the two topics, upload status + times,
  anything that needs him (e.g. Chrome was closed). No long reports.
