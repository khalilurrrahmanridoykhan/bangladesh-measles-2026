"""
Fix deaths extraction from DGHS measles PDFs.
The original scraper missed the deaths row. This script re-downloads
each PDF and extracts the 4-column deaths table specifically.

Deaths pattern in PDF (Page 1):
  [suspected_deaths_24h]  [suspected_deaths_cumulative]
  [confirmed_deaths_24h]  [confirmed_deaths_cumulative]
Appears as a single line: e.g.  "6 504 ০ ৯০"
"""

import requests
import urllib3
import pdfplumber
import pandas as pd
import io
import re
import json
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://dghs.gov.bd"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

DATA_DIR = "/Users/khalilur/Documents/AIWORK"


def bn2en(text: str) -> str:
    return text.translate(BANGLA_DIGITS)


def get_pdf_url(detail_url: str) -> str:
    from bs4 import BeautifulSoup
    try:
        r = requests.get(detail_url, headers=HEADERS, verify=False, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        obj = soup.find("object", {"type": "application/pdf"})
        if obj and obj.get("data"):
            return obj["data"]
    except Exception:
        pass
    return ""


def extract_deaths(pdf_bytes: bytes) -> dict:
    """
    Extract 4 death metrics from the PDF:
      suspected_deaths_24h, suspected_deaths_cumulative,
      confirmed_deaths_24h, confirmed_deaths_cumulative
    """
    result = {
        "suspected_deaths_24h": None,
        "suspected_deaths_cumulative": None,
        "confirmed_deaths_24h": None,
        "confirmed_deaths_cumulative": None,
    }
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Only need page 1
            page_text = pdf.pages[0].extract_text() or ""
    except Exception as e:
        print(f"    PDF parse error: {e}")
        return result

    lines = [ln.strip() for ln in page_text.split("\n") if ln.strip()]

    # Strategy: find a line (or adjacent lines) that:
    #   - contains "মৃত্যু" (death) keyword nearby
    #   - has exactly 4 numbers when extracted
    # The deaths section is always after the main suspect/confirm row on page 1.

    death_section_started = False
    for i, line in enumerate(lines):
        en_line = bn2en(line)

        # Trigger: once we see "মৃত্যু" in a header-like line, watch next few lines
        if "মৃত্যু" in line and not death_section_started:
            death_section_started = True

        if not death_section_started:
            continue

        # Extract all digit groups from this line
        nums = re.findall(r"\d+", en_line)
        if len(nums) == 4:
            vals = [int(n) for n in nums]
            # Sanity: cumulative (index 1) should be > daily (index 0)
            # and both should be plausible death counts (< 5000)
            if vals[1] >= vals[0] and vals[1] < 5000 and vals[3] < vals[1]:
                result["suspected_deaths_24h"] = vals[0]
                result["suspected_deaths_cumulative"] = vals[1]
                result["confirmed_deaths_24h"] = vals[2]
                result["confirmed_deaths_cumulative"] = vals[3]
                return result

        # Also try combining this line with the next
        if i + 1 < len(lines):
            combined = en_line + " " + bn2en(lines[i + 1])
            nums = re.findall(r"\d+", combined)
            if len(nums) == 4:
                vals = [int(n) for n in nums]
                if vals[1] >= vals[0] and vals[1] < 5000 and vals[3] < vals[1]:
                    result["suspected_deaths_24h"] = vals[0]
                    result["suspected_deaths_cumulative"] = vals[1]
                    result["confirmed_deaths_24h"] = vals[2]
                    result["confirmed_deaths_cumulative"] = vals[3]
                    return result

    return result


def main():
    # Load the scraped JSON which has detail URLs
    with open(f"{DATA_DIR}/dghs_measles_data.json", encoding="utf-8") as f:
        entries = json.load(f)

    # Load the existing national summary CSV
    df = pd.read_csv(f"{DATA_DIR}/measles_national_summary.csv")
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    deaths_records = {}

    print(f"Processing {len(entries)} press releases for deaths data...")
    for i, entry in enumerate(entries, 1):
        date = entry["date"]
        detail_url = entry.get("detail_url", "")
        if not detail_url:
            continue

        print(f"  [{i:02d}/{len(entries)}] {date}", end=" ... ", flush=True)

        pdf_url = get_pdf_url(detail_url)
        if not pdf_url:
            print("no PDF URL")
            continue

        try:
            r = requests.get(pdf_url, headers=HEADERS, verify=False, timeout=60)
            pdf_bytes = r.content
        except Exception as e:
            print(f"download failed: {e}")
            continue

        deaths = extract_deaths(pdf_bytes)
        deaths_records[date] = deaths

        d24 = deaths["suspected_deaths_24h"]
        dcum = deaths["suspected_deaths_cumulative"]
        c24 = deaths["confirmed_deaths_24h"]
        ccum = deaths["confirmed_deaths_cumulative"]
        print(f"susp_24h={d24}, susp_cum={dcum}, conf_24h={c24}, conf_cum={ccum}")
        time.sleep(0.2)

    # Patch the dataframe
    for date, deaths in deaths_records.items():
        mask = df["Date"] == date
        if mask.any():
            df.loc[mask, "Suspected Deaths (24h)"] = deaths["suspected_deaths_24h"]
            df.loc[mask, "Suspected Deaths (Cumulative)"] = deaths["suspected_deaths_cumulative"]
            df.loc[mask, "Confirmed Deaths (24h)"] = deaths["confirmed_deaths_24h"]
            df.loc[mask, "Confirmed Deaths (Cumulative)"] = deaths["confirmed_deaths_cumulative"]

    # Save updated CSV
    df.to_csv(f"{DATA_DIR}/measles_national_summary.csv", index=False, encoding="utf-8-sig")
    print(f"\nUpdated CSV saved: {DATA_DIR}/measles_national_summary.csv")

    # Show deaths summary
    filled = df["Suspected Deaths (Cumulative)"].notna().sum()
    print(f"Deaths filled: {filled}/{len(df)} rows")
    print(df[["Date", "Suspected Deaths (24h)", "Suspected Deaths (Cumulative)",
              "Confirmed Deaths (24h)", "Confirmed Deaths (Cumulative)"]].dropna().tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
