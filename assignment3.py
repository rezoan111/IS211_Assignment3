import argparse
import csv
import re
import sys
from datetime import datetime
from urllib.request import urlretrieve

DEFAULT_URL = "http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv"


def detect_browser(user_agent: str) -> str:
    ua = user_agent or ""

    # Order matters: Chrome UA often contains "Safari" too
    if re.search(r"Firefox", ua, re.IGNORECASE):
        return "Firefox"
    if re.search(r"Chrome", ua, re.IGNORECASE):
        return "Chrome"
    if re.search(r"MSIE|Trident", ua, re.IGNORECASE):
        return "Internet Explorer"
    if re.search(r"Safari", ua, re.IGNORECASE) and not re.search(r"Chrome", ua, re.IGNORECASE):
        return "Safari"

    return "Other"


def extract_hour(dt_str: str):
    """
    Return hour (0-23) from dt_str, or None if cannot parse.
    Tries common datetime formats, then falls back to regex hour extraction.
    """
    if not dt_str:
        return None

    dt_str = dt_str.strip()

    # Try common formats
    formats = (
        "%m/%d/%Y %H:%M:%S",  # 01/27/2014 03:26:04
        "%m/%d/%Y %H:%M",     # 01/27/2014 03:26
        "%Y-%m-%d %H:%M:%S",  # 2014-01-27 03:26:04
        "%Y-%m-%d %H:%M",     # 2014-01-27 03:26
    )
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt).hour
        except ValueError:
            pass

    # Fallback: pull hour from something like "03:26" or "3:26:04"
    m = re.search(r"\b(\d{1,2}):\d{2}(:\d{2})?\b", dt_str)
    if m:
        hour = int(m.group(1))
        if 0 <= hour <= 23:
            return hour

    return None


def main():
    parser = argparse.ArgumentParser(description="IS211 Week 3 - Text Processing")
    parser.add_argument("--url", required=False, default=DEFAULT_URL, help="URL to the weblog CSV file")
    args = parser.parse_args()

    local_file = "weblog.csv"

    # 1) Download CSV
    try:
        urlretrieve(args.url, local_file)
    except Exception as e:
        print(f"Error downloading file from URL: {args.url}")
        print(f"Details: {e}")
        sys.exit(1)

    # Regex for image hits (only if path ends with jpg/gif/png)
    img_re = re.compile(r"\.(jpg|gif|png)$", re.IGNORECASE)

    total_hits = 0
    image_hits = 0

    browser_counts = {
        "Firefox": 0,
        "Chrome": 0,
        "Internet Explorer": 0,
        "Safari": 0,
        "Other": 0,
    }

    hourly_hits = {h: 0 for h in range(24)}  # extra credit

    # 2) Read CSV and store in memory
    rows = []
    with open(local_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, skipinitialspace=True)
        for row in reader:
            if len(row) < 3:
                continue

            path = row[0].strip()
            dt_str = row[1].strip()
            user_agent = row[2].strip()

            rows.append((path, dt_str, user_agent))
            total_hits += 1

    # 3) Process stored data
    for path, dt_str, user_agent in rows:
        # Part III: image hits
        if img_re.search(path):
            image_hits += 1

        # Part IV: most popular browser
        b = detect_browser(user_agent)
        browser_counts[b] += 1

        # Part VI (Extra Credit): hourly hits
        hour = extract_hour(dt_str)
        if hour is not None:
            hourly_hits[hour] += 1

    # Output: Image percent
    percent = (image_hits / total_hits * 100) if total_hits else 0.0
    print(f"Image requests account for {percent:.1f}% of all requests")

    # Output: Most popular browser (ONLY among the 4 required)
    main_browsers = {k: v for k, v in browser_counts.items() if k != "Other"}
    popular_browser = max(main_browsers, key=main_browsers.get)
    print(f"Most popular browser is {popular_browser}")

    # Extra credit output: hours sorted by hits desc
    sorted_hours = sorted(hourly_hits.items(), key=lambda x: x[1], reverse=True)
    for hour, hits in sorted_hours:
        print(f"Hour {hour:02d} has {hits} hits")


if __name__ == "__main__":
    main()
