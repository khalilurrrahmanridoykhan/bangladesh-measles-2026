"""
DGHS Bangladesh - Measles (হাম) Full Data Extractor
Downloads all press release PDFs and extracts structured data in English.
Outputs: CSV + Excel with daily summary, division breakdown, and vaccination data.
"""

import requests
import urllib3
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
import io
import re
import time
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://dghs.gov.bd"
PRESS_RELEASE_URL = f"{BASE_URL}/pages/press-releases/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# Division names: Bangla → English
DIVISION_MAP = {
    "ঢাকা": "Dhaka", "রাজশাহী": "Rajshahi", "সিলেট": "Sylhet",
    "বরিশাল": "Barishal", "চট্টগ্রাম": "Chattogram", "ময়মনসিংহ": "Mymensingh",
    "খুলনা": "Khulna", "রংপুর": "Rangpur", "মোট": "Total",
    # OCR variations
    "বসিশাে": "Barishal", "িাজশাহী": "Rajshahi", "ময়মননসংহ": "Mymensingh",
    "খুেনা": "Khulna", "িংপুি": "Rangpur", "সমাট": "Total",
    "িিংপুি": "Rangpur", "িাজশাহী ": "Rajshahi",
}

# City Corporation names
CITYCORP_MAP = {
    "বরিশাল সিটি কর্পোরেশন": "Barishal CC",
    "চট্টগ্রাম সিটি কর্পোরেশন": "Chattogram CC",
    "কুমিল্লা সিটি কর্পোরেশন": "Cumilla CC",
    "ঢাকা উত্তর সিটি কর্পোরেশন": "Dhaka North CC",
    "ঢাকা দক্ষিণ সিটি কর্পোরেশন": "Dhaka South CC",
    "গাজীপুর সিটি কর্পোরেশন": "Gazipur CC",
    "নারায়নগঞ্জ সিটি কর্পোরেশন": "Narayanganj CC",
    "খুলনা সিটি কর্পোরেশন": "Khulna CC",
    "ময়মনসিংহ সিটি কর্পোরেশন": "Mymensingh CC",
    "রাজশাহী সিটি কর্পোরেশন": "Rajshahi CC",
    "রংপুর সিটি কর্পোরেশন": "Rangpur CC",
    "সিলেট সিটি কর্পোরেশন": "Sylhet CC",
    # OCR variations
    "বসিশাে সিটি ক্ল্াপলিশন": "Barishal CC",
    "চট্টগ্রাম সিটি ক্ল্াপলিশন": "Chattogram CC",
    "কুসমল্লা সিটি ক্ল্াপলিশন": "Cumilla CC",
    "ঢাক্া উত্তি সিটি ক্ল্াপলিশন": "Dhaka North CC",
    "ঢাক্া দসক্ষ্ন সিটি ক্ল্াপলিশন": "Dhaka South CC",
    "গাজীপুি সিটি ক্ল্াপলিশন": "Gazipur CC",
    "নািায়নগঞ্জ সিটি ক্ল্াপলিশন": "Narayanganj CC",
    "খুেনা সিটি ক্ল্াপলিশন": "Khulna CC",
    "ময়মনসিিংহ সিটি ক্ল্াপলিশন": "Mymensingh CC",
    "িাজশাহী সিটি ক্ল্াপলিশন": "Rajshahi CC",
    "িিংপুি সিটি ক্ল্াপলিশন": "Rangpur CC",
    "সিলেট সিটি ক্ল্াপলিশন": "Sylhet CC",
    "দমাট": "Total",
}


def bn2en(text: str) -> str:
    return text.translate(BANGLA_DIGITS).strip()


def clean_num(s: str) -> str:
    s = bn2en(s)
    s = re.sub(r"[,،\s]", "", s)
    return s if re.match(r"^\d+$", s) else ""


def parse_date(s: str) -> str:
    s = bn2en(s).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s


# ─── Network helpers ────────────────────────────────────────────────────────

def get_soup(url: str, params=None) -> BeautifulSoup | None:
    try:
        r = requests.get(url, params=params, headers=HEADERS, verify=False, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as e:
        print(f"    [WARN] {url}: {e}")
        return None


def get_pdf_bytes(url: str) -> bytes | None:
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=60)
        r.raise_for_status()
        return r.content
    except requests.RequestException as e:
        print(f"    [WARN] PDF download failed: {e}")
        return None


# ─── Listing scraper ─────────────────────────────────────────────────────────

def get_measles_listing(page_size: int = 100) -> list[dict]:
    entries, page = [], 1
    print("Collecting press release listing...")
    while True:
        soup = get_soup(PRESS_RELEASE_URL, {"page": page, "page_size": page_size})
        if not soup:
            break
        rows = soup.select("table tbody tr") or soup.select("tr")
        if not rows:
            break
        found = 0
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            title = cells[1].get_text(strip=True)
            if "হাম" not in title:
                continue
            link_tag = cells[-1].find("a") or cells[1].find("a")
            href = link_tag["href"] if link_tag else ""
            detail_url = href if href.startswith("http") else BASE_URL + href
            entries.append({
                "serial": bn2en(cells[0].get_text(strip=True)),
                "title_bangla": title,
                "date": parse_date(cells[2].get_text(strip=True)),
                "detail_url": detail_url,
            })
            found += 1
        print(f"  Page {page}: {found} entries (total {len(entries)})")
        # Pagination check
        nxt = soup.find("a", string=re.compile(r"next|›|»|পরবর্তী", re.I))
        if not nxt:
            break
        page += 1
        time.sleep(0.4)
    return entries


def get_pdf_url(detail_url: str) -> str:
    soup = get_soup(detail_url)
    if not soup:
        return ""
    obj = soup.find("object", {"type": "application/pdf"})
    if obj and obj.get("data"):
        return obj["data"]
    pdf_a = soup.find("a", href=re.compile(r"\.pdf", re.I))
    return pdf_a["href"] if pdf_a else ""


# ─── PDF parser ──────────────────────────────────────────────────────────────

def extract_numbers_from_line(line: str) -> list[str]:
    """Return all comma-separated or space-separated numbers on a line."""
    line = bn2en(line)
    nums = re.findall(r"[\d,،]+", line)
    return [n.replace(",", "").replace("،", "") for n in nums if re.search(r"\d", n)]


def parse_pdf(pdf_bytes: bytes, date: str) -> dict:
    """Parse a measles daily press release PDF into structured English data."""
    result = {
        "date": date,
        # National summary – last 24 hours
        "suspected_24h": None,
        "confirmed_24h": None,
        "suspected_deaths_24h": None,
        "confirmed_deaths_24h": None,
        # National summary – cumulative (from 15-Mar-2026)
        "suspected_cumulative": None,
        "confirmed_cumulative": None,
        "hospitalized_cumulative": None,
        "recovered_cumulative": None,
        "suspected_deaths_cumulative": None,
        "confirmed_deaths_cumulative": None,
        # Division rows and vaccination rows appended separately
        "_division_rows": [],
        "_vacc_division_rows": [],
        "_vacc_citycorp_rows": [],
    }

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = "\n".join(
                p.extract_text() or "" for p in pdf.pages
            )
    except Exception as e:
        print(f"    [WARN] PDF parse error: {e}")
        return result

    lines = [ln.strip() for ln in all_text.split("\n") if ln.strip()]
    bn_lines = lines  # keep original for matching

    # ── Helper: find first line matching a keyword and extract its numbers ──
    def nums_after(keyword_re: str, window: int = 3) -> list[str]:
        for i, ln in enumerate(lines):
            if re.search(keyword_re, ln, re.IGNORECASE):
                combined = " ".join(lines[i: i + window])
                return extract_numbers_from_line(combined)
        return []

    # ── Page-1 national summary ──
    # Row 1 – suspected/confirmed/hospitalized/recovered (4 big numbers)
    # The table header contains: সন্দেহজনক শনাক্ত | নিশ্চিত শনাক্ত | ভর্তির সংখ্যা | সুস্থ
    # Find a line with 6 numbers that look like case counts
    for i, ln in enumerate(lines):
        nums = extract_numbers_from_line(bn2en(ln))
        if len(nums) == 6 and all(n.isdigit() for n in nums):
            # Pattern: suspected_24h, suspected_cum, confirmed_24h, confirmed_cum, hospitalized_cum, recovered_cum
            vals = [int(n) for n in nums]
            if vals[1] > 1000:  # sanity: cumulative > 1000
                result["suspected_24h"] = vals[0]
                result["suspected_cumulative"] = vals[1]
                result["confirmed_24h"] = vals[2]
                result["confirmed_cumulative"] = vals[3]
                result["hospitalized_cumulative"] = vals[4]
                result["recovered_cumulative"] = vals[5]
                break

    # Deaths row – 4 numbers
    for i, ln in enumerate(lines):
        if "মৃত্যু" in ln or "মৃত" in ln:
            # Look ahead for a line with 4 numbers
            for j in range(i, min(i + 5, len(lines))):
                nums = extract_numbers_from_line(bn2en(lines[j]))
                if len(nums) >= 4 and all(n.isdigit() for n in nums[:4]):
                    vals = [int(n) for n in nums[:4]]
                    # suspected_24h_deaths, suspected_cum_deaths, confirmed_24h_deaths, confirmed_cum_deaths
                    if vals[1] > vals[0]:  # cumulative > daily: sanity check
                        result["suspected_deaths_24h"] = vals[0]
                        result["suspected_deaths_cumulative"] = vals[1]
                        result["confirmed_deaths_24h"] = vals[2]
                        result["confirmed_deaths_cumulative"] = vals[3]
                        break
            break

    # ── Page-2 division table ──
    # Each row: Division | 24h_suspected | 24h_deaths | 24h_hospitalized | 24h_conf_deaths | 24h_recovered
    #                    | cum_suspected | cum_confirmed | cum_hospitalized | cum_deaths | cum_recovered
    # We'll collect any line that starts with a known division name
    all_div_names = set(DIVISION_MAP.keys())
    for i, ln in enumerate(lines):
        matched_div = None
        for bn, en in DIVISION_MAP.items():
            if ln.startswith(bn) or ln == bn:
                matched_div = en
                break
        if not matched_div:
            continue
        # Gather numbers from this line + next line if needed
        combined = bn2en(ln) + " " + bn2en(lines[i + 1] if i + 1 < len(lines) else "")
        nums = [n for n in extract_numbers_from_line(combined) if n.isdigit()]
        if len(nums) >= 10:
            result["_division_rows"].append({
                "date": date,
                "division": matched_div,
                "suspected_24h": int(nums[0]),
                "suspected_deaths_24h": int(nums[1]),
                "hospitalized_24h": int(nums[2]),
                "confirmed_deaths_24h": int(nums[3]),
                "recovered_24h": int(nums[4]),
                "suspected_cumulative": int(nums[5]),
                "confirmed_cumulative": int(nums[6]),
                "hospitalized_cumulative": int(nums[7]),
                "confirmed_deaths_cumulative": int(nums[8]),
                "recovered_cumulative": int(nums[9]),
            })

    # ── Vaccination division table ──
    # Columns: Division | Target | Achieved | Coverage %
    in_vacc_div = False
    in_vacc_cc = False
    for i, ln in enumerate(lines):
        # Section headers
        if "হাম রুলবো ক্যালেইন" in ln or "হাম-রুবেলা ক্যাম্পেইন" in ln or "ক্যামপেইন" in ln:
            if "সিটি" in ln or "সিটি ক্ল্াপলিশন" in ln or "City" in ln:
                in_vacc_cc = True
                in_vacc_div = False
            else:
                in_vacc_div = True
                in_vacc_cc = False
            continue

        if in_vacc_div or in_vacc_cc:
            # Try division rows
            if in_vacc_div:
                for bn, en in DIVISION_MAP.items():
                    if ln.startswith(bn):
                        nums = extract_numbers_from_line(bn2en(ln))
                        if len(nums) >= 2:
                            coverage_raw = nums[2] if len(nums) > 2 else ""
                            result["_vacc_division_rows"].append({
                                "date": date,
                                "division": en,
                                "target": int(nums[0]) if nums[0].isdigit() else None,
                                "vaccinated": int(nums[1]) if nums[1].isdigit() else None,
                                "coverage_pct": int(coverage_raw.replace("%", "")) if coverage_raw.rstrip("%").isdigit() else None,
                            })
                        break
            if in_vacc_cc:
                for bn, en in CITYCORP_MAP.items():
                    if ln.startswith(bn) or bn in ln:
                        nums = extract_numbers_from_line(bn2en(ln))
                        if len(nums) >= 2:
                            coverage_raw = nums[2] if len(nums) > 2 else ""
                            result["_vacc_citycorp_rows"].append({
                                "date": date,
                                "city_corporation": en,
                                "target": int(nums[0]) if nums[0].isdigit() else None,
                                "vaccinated": int(nums[1]) if nums[1].isdigit() else None,
                                "coverage_pct": int(coverage_raw.replace("%", "")) if coverage_raw.rstrip("%").isdigit() else None,
                            })
                        break

    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("DGHS Bangladesh – Measles (হাম) Full Data Extractor")
    print("=" * 65)

    entries = get_measles_listing(page_size=100)
    print(f"\nTotal press releases: {len(entries)}")

    national_rows = []
    division_rows = []
    vacc_div_rows = []
    vacc_cc_rows = []

    for idx, entry in enumerate(entries, 1):
        date = entry["date"]
        print(f"  [{idx:02d}/{len(entries)}] {date} – fetching PDF...", end=" ", flush=True)

        pdf_url = get_pdf_url(entry["detail_url"])
        if not pdf_url:
            print("no PDF found, skipping.")
            continue

        pdf_bytes = get_pdf_bytes(pdf_url)
        if not pdf_bytes:
            print("download failed, skipping.")
            continue

        parsed = parse_pdf(pdf_bytes, date)
        print(
            f"suspects={parsed['suspected_24h']}, "
            f"confirmed={parsed['confirmed_24h']}, "
            f"deaths={parsed['suspected_deaths_24h']}"
        )

        # National summary row
        national_rows.append({
            "Date": date,
            "Suspected Cases (24h)": parsed["suspected_24h"],
            "Suspected Cases (Cumulative)": parsed["suspected_cumulative"],
            "Confirmed Cases (24h)": parsed["confirmed_24h"],
            "Confirmed Cases (Cumulative)": parsed["confirmed_cumulative"],
            "Hospitalized (Cumulative)": parsed["hospitalized_cumulative"],
            "Recovered (Cumulative)": parsed["recovered_cumulative"],
            "Suspected Deaths (24h)": parsed["suspected_deaths_24h"],
            "Suspected Deaths (Cumulative)": parsed["suspected_deaths_cumulative"],
            "Confirmed Deaths (24h)": parsed["confirmed_deaths_24h"],
            "Confirmed Deaths (Cumulative)": parsed["confirmed_deaths_cumulative"],
            "Press Release URL": entry["detail_url"],
            "PDF URL": pdf_url,
        })

        division_rows.extend(parsed["_division_rows"])
        vacc_div_rows.extend(parsed["_vacc_division_rows"])
        vacc_cc_rows.extend(parsed["_vacc_citycorp_rows"])

        time.sleep(0.3)

    # ── Build DataFrames ──
    df_national = pd.DataFrame(national_rows).sort_values("Date")
    df_division = pd.DataFrame(division_rows).sort_values(["date", "division"]) if division_rows else pd.DataFrame()
    df_vacc_div = pd.DataFrame(vacc_div_rows).sort_values(["date", "division"]) if vacc_div_rows else pd.DataFrame()
    df_vacc_cc = pd.DataFrame(vacc_cc_rows).sort_values(["date", "city_corporation"]) if vacc_cc_rows else pd.DataFrame()

    # ── Save Excel (multi-sheet) ──
    out_dir = "/Users/khalilur/Documents/AIWORK"
    xlsx_path = f"{out_dir}/dghs_measles_data_EN.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_national.to_excel(writer, sheet_name="National Summary", index=False)
        if not df_division.empty:
            df_division.to_excel(writer, sheet_name="Division Breakdown", index=False)
        if not df_vacc_div.empty:
            df_vacc_div.to_excel(writer, sheet_name="Vaccination by Division", index=False)
        if not df_vacc_cc.empty:
            df_vacc_cc.to_excel(writer, sheet_name="Vaccination by City Corp", index=False)

    # ── Save CSVs ──
    df_national.to_csv(f"{out_dir}/measles_national_summary.csv", index=False, encoding="utf-8-sig")
    if not df_division.empty:
        df_division.to_csv(f"{out_dir}/measles_division_breakdown.csv", index=False, encoding="utf-8-sig")
    if not df_vacc_div.empty:
        df_vacc_div.to_csv(f"{out_dir}/measles_vaccination_division.csv", index=False, encoding="utf-8-sig")
    if not df_vacc_cc.empty:
        df_vacc_cc.to_csv(f"{out_dir}/measles_vaccination_citycorp.csv", index=False, encoding="utf-8-sig")

    print(f"\n{'='*65}")
    print(f"Saved: {xlsx_path}")
    print(f"       {out_dir}/measles_national_summary.csv")
    print(f"       {out_dir}/measles_division_breakdown.csv")
    print(f"\n── National Summary Preview ──")
    print(df_national[["Date", "Suspected Cases (24h)", "Suspected Cases (Cumulative)",
                        "Confirmed Cases (24h)", "Suspected Deaths (24h)", "Suspected Deaths (Cumulative)"]].to_string(index=False))


if __name__ == "__main__":
    main()
