# Daily Quote Telegram Bot
> Send daily reality-based quotes via Telegram.

<p align="center">
  <img src="assets/demo.gif">
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/tuananh511/telegram-reality-bot?label=release" alt="Release">
  <img src="https://img.shields.io/github/license/tuananh511/telegram-reality-bot" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/tuananh511/telegram-reality-bot/main.yml?label=build" alt="Build">
</p>

## Overview
A Telegram bot that automatically sends short, reflective Vietnamese quotes with a real-life, mature tone — similar to healing captions and reflections on life, family, loneliness, time, and personal growth. If a special day occurs (holiday, anniversary, international event), the bot automatically attaches a notice above the quote. The system runs entirely on GitHub Actions on a cron schedule, with no VPS or dedicated server required.

## Features
- Sends quotes automatically on a schedule
- Prevents duplicate content
- Automatically detects special events on the current day
- Randomizes sending frequency to avoid spamming
- Stays silent during quiet hours (23:00 → 08:00)
- No VPS required
- Runs at near-zero cost

**AI used:** Google Gemini API (`gemini-3.1-flash-lite`) — generates natural Vietnamese quotes, reduces the "AI quote machine" feel, produces content in the style of reflective Facebook captions, and checks for special events on the day.

**Tech stack:** Python · GitHub Actions · Telegram Bot API · Google Gemini API · JSON state tracking

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/tuananh511/telegram-reality-bot.git
   cd telegram-reality-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the required secrets/environment variables (Telegram bot token, chat ID, Gemini API key) — for GitHub Actions, add them under **Settings → Secrets and variables → Actions**.

## Usage
The bot is designed to run via the scheduled GitHub Actions workflow in `.github/workflows`:
- The workflow runs every 2 hours.
- Outside the 08:00–23:00 window, the bot skips sending.
- On each run, it checks for a special event, picks a random emotional theme, generates a new quote via Gemini, checks against duplicates, then decides whether to send (always if there's an event, otherwise a random 15% chance).
- State is persisted in `used_messages.json` and `event_sent.json`.

To run locally instead of via Actions:
```bash
python main.py
```

**Rotating themes:** family, growing up, being a man, loneliness, life pressure, kindness, time, youth, quiet perseverance, peace, healing, loss, the journey of growing up, responsibility, late-night thoughts.

## Roadmap
- [ ] Habit tracking
- [ ] Reminders
- [ ] AI companion mode
- [ ] Personal assistant layer

> Note: this project is currently designed for single-user, personal use. Since it relies on GitHub Actions cron instead of a real-time server, it's best suited for forking/self-hosting rather than scaling into a public multi-user bot (which would need a VPS or a webhook/polling server running 24/7).

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
