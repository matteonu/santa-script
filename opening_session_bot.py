"""
Opening Session + St. Nicholas Express watcher - Verbier 4Vallees
Every minute (07:00-20:00) it opens the page, clicks "Book now", and checks
whether the date list says "Sold out!". When it doesn't anymore it shows a
big red full-screen alert and opens the page in your browser.

Setup (once):
    pip install playwright
    python -m playwright install chromium
"""

import re
import time
import datetime
import webbrowser
import tkinter as tk

from playwright.sync_api import sync_playwright

URL = "https://verbier4vallees.ch/en/online-shop/activities/opening-session-st.nicholas-express_activity_426820"
ACTIVITY_ID = "426820"
CHECK_EVERY_SECONDS = 60
START_HOUR = 0    # 07:00
END_HOUR = 24     # 20:00


def log(msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)


def check_once(page):
    """Returns True = still sold out, False = AVAILABLE, None = couldn't tell."""
    page.goto(URL, wait_until="domcontentloaded", timeout=45000)

    book_btn = page.locator(
        f'[data-activity-ticket-config-id="{ACTIVITY_ID}"] '
        'button.js-activity-ticket-config__open:visible'
    ).first
    book_btn.wait_for(state="visible", timeout=20000)

    # The site's JS attaches the click handler after load, so retry a few times.
    choose_date = page.get_by_text("choose date", exact=False).first
    opened = False
    for _ in range(4):
        book_btn.evaluate("el => el.click()")   # JS click ignores cookie banners
        try:
            choose_date.wait_for(state="visible", timeout=5000)
            opened = True
            break
        except Exception:
            pass
    if not opened:
        log("Booking popup didn't open")
        return None

    sold_out = page.get_by_text("Sold out!", exact=True)
    try:
        sold_out.first.wait_for(state="visible", timeout=10000)
        return True
    except Exception:
        pass

    # No "Sold out!" - make sure the date list actually loaded before alerting.
    dates = page.get_by_text(re.compile(r"\d{1,2}/\d{1,2}/\d{4}"))
    if dates.count() > 0:
        return False
    log("Date list didn't load")
    return None


def big_red_alert():
    webbrowser.open(URL)
    root = tk.Tk()
    root.title("TICKETS AVAILABLE - St. Nicholas Express")
    root.configure(bg="red")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    tk.Label(root, text="ST. NICHOLAS EXPRESS\nNOT SOLD OUT!\nBOOK NOW!",
             fg="white", bg="red", font=("Helvetica", 72, "bold")).pack(expand=True)
    tk.Label(root, text="(click anywhere or press Esc to close)",
             fg="white", bg="red", font=("Helvetica", 20)).pack(pady=40)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Button-1>", lambda e: root.destroy())

    def beep(n=0):
        if n < 20:
            root.bell()
            root.after(500, beep, n + 1)
    beep()
    root.focus_force()
    root.mainloop()


def main():
    log("Watcher started")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"),
        )
        page = context.new_page()

        while True:
            hour = datetime.datetime.now().hour
            if START_HOUR <= hour < END_HOUR:
                try:
                    result = check_once(page)
                    if result is True:
                        log("Still sold out")
                    elif result is False:
                        log("NOT SOLD OUT ANYMORE!")
                        big_red_alert()
                        break
                except Exception as e:
                    log(f"Check failed, will retry: {e}")
            time.sleep(CHECK_EVERY_SECONDS)

        browser.close()


if __name__ == "__main__":
    main()
