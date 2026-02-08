import argparse
import csv
import re
import sys
from datetime import datetime
from urllib.request import urlretrieve


DEFAULT_URL = "http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv"


def detect_browser(user_agent: str) -> str:
    ua = user_agent or ""

    # Order matters:
    # Chrome UA usually contains "Safari" too, so check Chrome first.
    if re.search(r"Firefox", ua, re.IGNORECASE):
        return "Firefox"
    if re.search(r"Chrome", ua, re.IGNORECASE):
        return "Chrome"
    # Internet Explorer patterns
    if re.search(r"MSIE|Trident", ua, re.IGNORECASE):
        return "Internet Explorer"
    # Safari (but not Chrome)
    if re.search(r"Safari", ua, re.IGNORECASE) and not re.search(r"Chrome", ua, re.IGNORECASE):
        return "Safari"

    return "Other"


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

    # Regex for image hits
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

    # 2) Read CSV
    # Example row:
    # /images/test.jpg, 01/27/2014 03:26:04, Mozilla/5.0 (Linux) Firefox/34.0, 200, 346547
    with open(local_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, skipinitialspace=True)
        rows = []

        for row in reader:
            if len(row) < 5:
                continue  # skip bad lines

            path = row[0].strip()
            dt_str = row[1].strip()
            user_agent = row[2].strip()
            # status = row[3].strip()  # not required for the tasks
            # size = row[4].strip()    # not required for the tasks

            rows.append((path, dt_str, user_agent))
            total_hits += 1

    # 3) Process stored data (in memory)
    for path, dt_str, user_agent in rows:
        # Part III: image hits
        if img_re.search(path):
            image_hits += 1

        # Part IV: most popular browser
        b = detect_browser(user_agent)
        browser_counts[b] += 1

        # Extra credit: hour counts
        try:
            dt = datetime.strptime(dt_str, "%m/%d/%Y %H:%M:%S")
            hourly_hits[dt.hour] += 1
        except ValueError:
            pass

    # Output: Image percent
    percent = (image_hits / total_hits * 100) if total_hits else 0.0
    print(f"Image requests account for {percent:.1f}% of all requests")

    # Output: Most popular browser (only among the 4 required, but we keep Other too)
    # If you want ONLY the 4, remove "Other" before max.
    popular_browser = max(browser_counts, key=browser_counts.get)
    print(f"Most popular browser is {popular_browser}")

    # Extra credit output: hours sorted by hits desc
    # Format like: Hour 12 has 1023 hits
    sorted_hours = sorted(hourly_hits.items(), key=lambda x: x[1], reverse=True)
    for hour, hits in sorted_hours:
        print(f"Hour {hour:02d} has {hits} hits")


if __name__ == "__main__":
    main()
   
