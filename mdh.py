from playwright.sync_api import Playwright, sync_playwright, expect
from time import sleep

from secrets import PASSWORD, EMAIL, LOCATION

def start_shift(playwright: Playwright, end_hour: str, end_minute: str) -> None:
    before_noon = int(end_hour) < 12
    if int(end_hour) > 12:
        end_hour = str(int(end_hour) - 12)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://beta.mydigitalhand.org/")
    page.locator("input[name=\"email\"]").click()
    page.locator("input[name=\"email\"]").fill(EMAIL)
    page.locator("input[name=\"password\"]").click()
    page.locator("input[name=\"password\"]").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("link", name="University of North Carolina").click()
    page.get_by_role("button", name="Waitlist").click()

    if page.get_by_text("Start shift").is_visible() is False:
        print("already running!")
        context.close()
        browser.close()
        return

    page.get_by_role("button", name="Start shift").click()
    
    page.locator("input[name=\"endMoment\"]").click()

    page.get_by_text("AM" if before_noon else "PM").click()
    
    hrButton = page.locator("//div[@class=\"MuiPickersTimePickerToolbar-hourMinuteLabel\"]//button[1]")
    minButton = page.locator("//div[@class=\"MuiPickersTimePickerToolbar-hourMinuteLabel\"]//button[2]")

    hrButton.click()

    box = page.get_by_text(str(end_hour)).last().bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

    minButton.click()

    box = page.get_by_text(str(end_minute)).last().bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

    page.get_by_role("button", name="OK").click()
    page.locator("input[name=\"location\"]").click()
    page.locator("input[name=\"location\"]").fill(LOCATION)
    page.get_by_role("button", name="Done").click()

    print("started shift")

    context.close()
    browser.close()

def end_shift(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://beta.mydigitalhand.org/")
    page.locator("input[name=\"email\"]").click()
    page.locator("input[name=\"email\"]").fill(EMAIL)
    page.locator("input[name=\"password\"]").click()
    page.locator("input[name=\"password\"]").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("link", name="University of North Carolina").click()
    page.get_by_role("button", name="Waitlist").click()

    page.get_by_role("button", name="End now").click()
    page.get_by_role("button", name="End shift now").click()

    print("ended shift")

    context.close()
    browser.close()

if __name__ == "__main__":
    times = []

    with open("/rushil/auto-mdh/schedule.csv") as f:
        for line in f:
            if line.startswith("Day"):
                continue
            day, start, end = line.split(",")
            start_hour, start_minute = start.split(":")
            end_hour, end_minute = end.split(":")
            day = int(day)

            start_minute, end_minute = start_minute.strip(), end_minute.strip()

            times.append((day, start_hour, start_minute, end_hour, end_minute))

    from datetime import datetime

    now = datetime.now()

    with sync_playwright() as playwright:
        for day, start_hour, start_minute, end_hour, end_minute in times:
            start_minutes = int(start_hour) * 60 + int(start_minute)
            end_minutes = int(end_hour) * 60 + int(end_minute)

            if day == now.weekday() and start_minutes <= now.hour * 60 + now.minute <= end_minutes:
                start_shift(playwright, end_hour, end_minute)