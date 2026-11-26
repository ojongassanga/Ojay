---
name: maison-lyaura-ad
description: Edit a Maison LyAura product video (pyjamas or other women's fashion) into a beat-synced Instagram/Facebook ad with the house caption style — animated brand name, swinging price tag centre-left, small captions under the price, and the dark animated end card with "Paiement à la livraison" and the phone number. Use whenever the user uploads a video and asks for captions, an ad edit, a re-edit "in the same format", a storyboard/scene board, or a final render for Maison LyAura.
---

# Maison LyAura ad edit

The proven workflow and house style from two approved ads (see `maison-lyaura-ad/` and
`maison-lyaura-ad-2/` in this repo for the finished videos and storyboards). Scripts in
`scripts/`, the graphics template in `templates/`.

## Brand constants (confirm each time, keep exact formats)

- Brand name: **Maison LyAura** (script font Pinyon Script). Opening subtitle: `PYJAMAS FEMME`.
- Price: **9,000frs**, written exactly like that (comma, lowercase "frs", no "seulement").
- End-card lines: **Paiement à la livraison**, then **683439278**, written exactly like that (no spaces).
- Captions in French. Sizes are written **M - 3XL**.

## Workflow (always in this order)

1. **Analyze** the upload: `python3 -I scripts/analyze.py VIDEO OUTDIR`, then read `OUTDIR/strip.jpg`.
   - It gives you the tempo and beat grid. Pick the downbeat as the beat position with the strongest kick and onset.
   - It also gives cut candidates and the drop (where the kick energy jumps).
   - Phone-app exports often have baked-in junk: colour/pink wipes, glow flashes, glitch frames, a black tail. Check the per-0.25s saturation (spikes inside a B&W shot) and the strip, and list the clean source range of every shot.
   - iPhone HDR (HLG/Dolby Vision) needs `"hdr": true` in the plan, which converts bt2020 to bt709.
2. **Storyboard first, never render before approval.**
   - Publish an HTML artifact with phone-shaped 9:16 frames using real stills, base64-embedded.
   - Mock the graphics on each frame with the same CSS. Animate the motions live (captions cycling out to the left, the swinging tag, the end card).
   - Add a beat timeline with the scenes and shots, a toggle for Instagram's covered zones (top 11%, bottom 20%, right 15% from 45-80% height), an edit decision list (new time, shot, source range, speed, transition) and a short "please confirm" list.
   - Keep the notes under each frame to one or two short lines; the client asked for less text. Copy `maison-lyaura-ad-2/storyboard.html` as the template.
   - Iterate until the client approves, publishing updates to the same artifact.
3. **Build the picture edit**: write a plan JSON like `templates/example_plan.json`, then run `python3 -I scripts/build_edit.py plan.json base.mp4`.
4. **Graphics**: write a config like `templates/example_config.json`, then run `node templates/render_overlay.js config.json ovdir`. This makes 720×1280 transparent PNGs, one per frame at 30 fps.
5. **Compose and encode**: `bash scripts/compose.sh base.mp4 ovdir SOURCE END_CARD_START DURATION out.mp4`
6. **Verify, then deliver.**
   - Sample frames across the timeline into a contact sheet and look at it, especially the transitions and the drop.
   - Check the duration and frame count.
   - Send the file with SendUserFile, and commit it with the storyboard and sources to a new `maison-lyaura-ad-N/` folder.

## Editing rules (client feedback, do not regress)

- **Every cut on the beat**: B(k) = first_beat + beat × k. Full looks change once per bar, on downbeats. Put the strongest moment (the price pulse) on the drop.
- **Fluid, never laggy or blurry.**
  - Clip speed 0.85-1.1×. Below 0.97× the script uses motion-compensated interpolation.
  - Never use `framerate` blending or `zoompan` push-ins on visible footage; they caused stutter and blur.
  - No `hblur` or `zoomin` transitions. On the drop use a hard cut plus `{"punch": true}`.
  - If the footage is too short to fill the beats, start the end card a bar earlier rather than slowing clips.
- **Transitions**: soft `fade` 0.3s on calm close-ups, `smoothleft`/`smoothright` 0.2-0.27s as whips that follow camera moves, and hard cuts (`fade` 0.067) on full-look changes.
- **Rebuild from clean ranges only.** Drop app ghosting, glow and glitch frames, and the black tail. Reorder shots to alternate the colourways.
- **Grade and finish**: light contrast/saturation, slightly warm, mild unsharp. Export 720×1280, 30 fps, H.264 high, CRF 16, ~10 Mbps, AAC 256k 48 kHz, faststart (all in compose.sh).
- **Music**: use the source's own audio, fade it out over the last ~1.5s, and never leave black at the end. If the clip is shorter than the music, the end card holds on a slow, blurred last shot.

## Graphics style (all in templates/overlay.html, driven by the config)

- **Opening (0 to about 3.3s)**:
  - Fade up from blush. "Maison LyAura" writes itself on in the centre on an ivory pill with gold edge, starting at the first downbeat, with a sparkle at the pen tip.
  - At `land` the name shrinks and glides into the small signature.
- **Price tag**:
  - It slides down from the top, growing gradually, and lands centre-left (left 5cqw, top 36%, not hugging the edge) at `land`.
  - It swings gently all ad long, one swing per bar. It pulses with gold sparkles on each beat during `pulse` (the drop).
- **Stack**: signature just above the price, caption just below. All three fade out together just before the end card. Nothing covers the product on the mannequin.
- **Captions**:
  - Small italic Cormorant on an ivory chip, directly under the price, all on one line.
  - Each one slides out to the left and fades on the next beat boundary, and the next fades in in the same spot.
  - Use `words` for lists that pop in one word per beat (e.g. `M · L · XL · 2XL · 3XL`).
- **End card**:
  - The video blurs under a deep wine radial veil. The client wanted it darker: `veil` is [0.68, 0.93].
  - The name writes itself on in champagne gold, then shimmers and floats continuously, never static.
  - Around it float a bow, moon, sleep mask, rose, pearls, hearts, falling petals and twinkles.
  - The payment line appears on a downbeat (`infoAt`) and the phone number one beat later. **No price on the end card.**

## Practical notes

- **Upload limit**: the chat upload limit is 30 MB. If the client can't upload, suggest sending the video to themselves on WhatsApp (it compresses it), trimming it, exporting 720p/1080p from iMovie, or splitting it in two.
- **Fonts**: they are bundled in `templates/fonts`, so no network is needed. Playwright and Chromium are preinstalled in cloud sessions.
- **Run time**: building the edit takes about 4-5 min (interpolation); the graphics take about 35s.
