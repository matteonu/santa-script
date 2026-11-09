# santa-script

Watches the **Opening Session + St. Nicholas Express** activity on the Verbier 4Vallées online shop and alerts you when it's no longer sold out.

Every minute it loads the page in headless Chromium, clicks **Book now**, and checks whether the date list still says "Sold out!". Once it doesn't, it opens the page in your browser and shows a full-screen red alert with beeps.

## Setup

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Run

```bash
python opening_session_bot.py
```

## Config

Edit the constants at the top of `opening_session_bot.py`:

- `URL` / `ACTIVITY_ID`: the activity to watch
- `CHECK_EVERY_SECONDS`: how often to check (default 60)
- `START_HOUR` / `END_HOUR`: the hours when checks run (default: all day)
