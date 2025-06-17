# 🎮 Brick Breaker — Built with Amazon Q Developer CLI 🧱

A retro‑inspired **Brick Breaker** arcade game that I created almost entirely by chatting with **Amazon Q Developer CLI**. This repo & write‑up are my submission for the *Build Games with Amazon Q CLI* T‑shirt challenge 👕.

---

## 📑 Table of contents

1. [Gameplay overview](#gameplay-overview-🎯)
2. [Screenshots](#screenshots-📸)
3. [Features](#features-✨)
4. [Controls](#controls-🕹️)
5. [Quick start](#quick-start-🚀)
6. [Prompts used](#prompts-used-💬)
7. [Lessons learned](#lessons-learned-🧠)
8. [Contributing](#contributing-🤝)
9. [License](#license-📜)

---

## Gameplay overview 🎯

Brick Breaker challenges you to clear colourful brick patterns with a bouncing ball while keeping your paddle in play. Four nostalgic power‑ups — **Wider Paddle**, **Sticky Paddle**, **Multi‑Ball**, and **Slow Motion** — spice things up across three handcrafted JSON levels. Everything runs at a silky‑smooth 60 FPS in a 1280 × 720 window using nothing but Python 3.12 + PyGame 2 🐍.

## Screenshots 📸

![Title screen](docs/screenshots/title.png)
![In‑game action](docs/screenshots/gameplay.png)

## Features ✨

- Classic paddle‑and‑ball mechanics with angle‑based reflections
- Three difficulty‑curated levels in **levels/** (easy to extend)
- Four configurable power‑ups (drop‑rate in `settings.py`)
- Heads‑Up Display for score, lives, level number, and power‑up timer
- Pause / restart support and game‑over screen
- 100 % Python 3.12 + PyGame 2 — no other deps
- Fully type‑hinted, PEP‑8‑compliant codebase with unit tests in **tests/**

## Controls 🕹️

| Key       | Action                  |
| --------- | ----------------------- |
| **← / →** | Move paddle             |
| **Space** | Launch or relaunch ball |
| **P**     | Pause / unpause         |
| **Esc**   | Quit                    |

## Quick start 🚀

```bash
# 1 · clone the repo
git clone https://github.com/<your‑user>/brick‑breaker.git
cd brick‑breaker

# 2 · create & activate a virtual environment (Ubuntu 24.04 ships Python 3.12)
sudo apt update && sudo apt install python3‑venv -y  # one‑time
python3 -m venv .venv
source .venv/bin/activate

# 3 · install requirements & run
pip install -r requirements.txt
python src/main.py
```

### Makefile shortcuts

```bash
make run    # activate venv + launch game
make test   # run pytest suite
```

## Prompts used 💬

Below are the **exact** prompts I sent to Amazon Q CLI — including them here satisfies the campaign’s “show your prompts” requirement.

```text
Hey Q! ✨ I’d love your help building a small retro‑style Brick Breaker game in Python 3.11
using PyGame. Please:

1. Explain—in plain English—how you’d structure the project (files, classes, game loop).
2. Generate an initial repo skeleton with empty or stubbed files so I can see the layout:
     • src/      (main.py, settings.py, etc.)
     • assets/   (make placeholder PNG + WAV if needed)
     • tests/
3. Produce a short README telling me how to create a virtualenv, install requirements,
   and run the game loop stub.
4. Keep the code runnable (`python src/main.py` should open a blank 800×600 window showing
   “Brick Breaker – Work in Progress” text).
No gameplay yet—just scaffolding and your plan. Thanks!
```

```text
Awesome, thanks! Let’s flesh it out:

🔸 Core mechanics
• Paddle, ball physics with angle reflection off walls and paddle.
• Three JSON level layouts stored in levels/ (rows, brick types).
• Score, lives, and a simple HUD.

🔸 Power‑ups (random drop % configurable in settings.py)
1. 🟥 Wider paddle (20 s)
2. 🟦 Sticky paddle (next hit lets me aim)
3. 🟩 Multi‑ball (adds two extra balls)
4. 🟨 Slow‑motion (ball speed 50 % for 10 s)

🔸 Art & audio
• Placeholder 32×16 pixel PNG sprites (solid colours OK).
• 8‑bit WAV sounds: bounce, brick_break, powerup, game_over.
• Use a free retro font (PressStart2P.ttf) for UI.

🔸 Engineering
• Constants in settings.py; use dataclasses where sensible.
• Keep every function ≤40 lines, PEP 8 compliant, type‑hinted.
• Add tests/test_collision.py covering ball‑brick & ball‑paddle maths (pytest).

Please update the existing files instead of rewriting from scratch, and make sure
`python src/main.py` now plays a full game at 60 FPS in a 1280×720 window. 🙌
```

```text
Last stretch! Could you:

1. Expand README with:
   • Setup commands (`python -m venv …`, `pip install -r requirements.txt`)
   • Run instructions
   • Packaging tip (`zip -r retro_brick_breaker.zip .`)
2. Give me a neat blog‑post outline (markdown - H2/H3) covering: idea, prompts used,
   screenshots placeholders, what I learned using Amazon Q CLI, how to claim the T‑shirt.
3. List the exact `q dev` commands someone could have run incrementally to create:
   • src/game_objects.py
   • levels/level_01.json
   • README.md
4. Finish with “ALL DONE” so I know you’re finished.

Keep total output <25 k tokens. Cheers! 🎉
```

## Lessons learned 🧠

- **Iterative prompting beats monoliths.** Splitting work across multiple prompts kept Q’s output coherent and modular. It helps in debugging code easy.
- **File‑aware agentic mode is 🔥.** Q wrote & updated individual files without clobbering unrelated code.
- **Small assets, fast repo.** Using CC‑0 pixel art prevents bloated pushes and makes reviewers happy.

## Contributing 🤝

Pull requests are welcome! Please open an issue first and describe the feature or bug you’re tackling.

## License 📜

This project is released under the MIT License. See [LICENSE](LICENSE) for full text.

