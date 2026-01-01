import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import os
from typing import Dict, List, Set, Tuple, Any, Optional

URL = "https://portal.wzss.pl/competitions/current"
LOCATIONS_CSV_FILE = "locations.csv"
COMPETITIONS_JSON_FILE = "competitions.json"
locations_competitions: Dict[Tuple[str, str], Dict[str, Any]] = {}


def sanitize_location(text: str) -> str:
    """Removes commas and quotes from a string."""
    return re.sub(r'[",]', "", text).strip()


def load_locations_data() -> Dict[str, Dict[str, Any]]:
    """Loads location data from the CSV file."""
    if not os.path.exists(LOCATIONS_CSV_FILE):
        return {}

    locations = {}
    try:
        with open(LOCATIONS_CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = (
                    float(row["latitude"])
                    if row["latitude"] and row["latitude"] != "None"
                    else None
                )
                lon = (
                    float(row["longitude"])
                    if row["longitude"] and row["longitude"] != "None"
                    else None
                )
                website = row.get("website", "")
                locations[row["location_text"]] = {
                    "latitude": lat,
                    "longitude": lon,
                    "website": website,
                }
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error loading {LOCATIONS_CSV_FILE}: {e}")
    return locations


def fetch_competitions_html() -> Optional[str]:
    """Fetches the competitions HTML from the URL."""
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {URL}: {e}")
        return None


def parse_competitions(
    html: str, locations_data: Dict[str, Dict[str, Any]]
) -> Tuple[Dict[Tuple[str, str], Dict[str, Any]], Set[str]]:
    """Parses the HTML to extract competition data."""
    soup = BeautifulSoup(html, "html.parser")

    all_locations: Set[str] = set()
    club_websites: Dict[str, str] = {}

    # First pass: collect all websites per club
    month_headers = soup.find_all("p", class_="text-2xl")
    for i, header in enumerate(month_headers):
        for sibling in header.find_next_siblings():
            if (
                sibling.name == "p"
                and "text-2xl" in sibling.get("class", [])
                and sibling != header
            ):
                break

            if "sm:grid-cols-12" in sibling.get("class", []):
                club_p = sibling.find("p", class_="uppercase")
                if not club_p:
                    continue
                club_name = club_p.contents[0].strip()

                regulation_a = None
                for a in sibling.find_all("a", href=True):
                    if "Regulamin" in a.get_text():
                        regulation_a = a
                        break

                if regulation_a:
                    try:
                        website = "/".join(regulation_a["href"].split("/")[:3])
                        if website and club_name not in club_websites:
                            club_websites[club_name] = website
                    except Exception:
                        pass

    # Second pass: build the competition structure
    for i, header in enumerate(month_headers):
        for sibling in header.find_next_siblings():
            if (
                sibling.name == "p"
                and "text-2xl" in sibling.get("class", [])
                and sibling != header
            ):
                break

            if "sm:grid-cols-12" in sibling.get("class", []):
                club_p = sibling.find("p", class_="uppercase")
                location_p = sibling.find("p", class_="leading-4")

                if not (club_p and location_p):
                    continue

                club_name = club_p.contents[0].strip()
                location_text = location_p.text.strip()
                sanitized_location = sanitize_location(location_text)
                all_locations.add(sanitized_location)

                website = club_websites.get(club_name, "")

                location_key = (club_name, sanitized_location)
                if location_key not in locations_competitions:
                    coords = locations_data.get(sanitized_location, {})

                    locations_competitions[location_key] = {
                        "club": club_name,
                        "location": location_text,
                        "latitude": coords.get("latitude"),
                        "longitude": coords.get("longitude"),
                        "website": website or coords.get("website", ""),
                        "competitions": [],
                    }

                # Update website if we found one (might have been empty from CSV)
                if website and not locations_competitions[location_key]["website"]:
                    locations_competitions[location_key]["website"] = website

                competition = {}
                date_div = sibling.find("div", class_="whitespace-nowrap")
                if date_div:
                    competition["date"] = date_div.text.strip()

                name_strong = sibling.find("strong", class_="leading-4")
                if name_strong:
                    competition["name"] = name_strong.text.strip()

                regulation_a = None
                for a in sibling.find_all("a", href=True):
                    if "Regulamin" in a.get_text():
                        regulation_a = a
                        break

                if regulation_a:
                    competition["regulation_link"] = regulation_a["href"]

                weapon_types_div = sibling.find("div", class_="grid-cols-2")
                if weapon_types_div:
                    weapons = [p.text.strip() for p in weapon_types_div.find_all("p")]
                    competition["weapons"] = weapons

                if competition:
                    locations_competitions[location_key]["competitions"].append(
                        competition
                    )

    return locations_competitions, all_locations


def save_competitions_json(competitions: List[Dict[str, Any]]):
    """Saves the competition data to a JSON file."""
    with open(COMPETITIONS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(competitions, f, ensure_ascii=False, indent=4)
    print(
        f"Successfully scraped {len(competitions)} locations and saved to {COMPETITIONS_JSON_FILE}"
    )


def update_locations_csv(
    all_locations: Set[str],
    locations_data: Dict[str, Dict[str, Any]],
    locations_competitions: Dict[Tuple[str, str], Dict[str, Any]],
):
    """Creates or updates the locations CSV file."""
    with open(LOCATIONS_CSV_FILE, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["location_text", "latitude", "longitude", "website"])
        for loc in sorted(list(all_locations)):
            coords = locations_data.get(loc, {})
            website = ""
            for k, v in locations_competitions.items():
                if sanitize_location(v["location"]) == loc:
                    if v.get("website"):
                        website = v["website"]
                        break
            if not website:
                website = coords.get("website", "")

            writer.writerow(
                [loc, coords.get("latitude", ""), coords.get("longitude", ""), website]
            )
    print(
        f"{LOCATIONS_CSV_FILE} file updated with {len(all_locations)} locations. Please fill in the missing coordinates."
    )


def main():
    """Main function to fetch, parse, and save competition data."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    global LOCATIONS_CSV_FILE
    global COMPETITIONS_JSON_FILE
    LOCATIONS_CSV_FILE = os.path.join(script_dir, LOCATIONS_CSV_FILE)
    COMPETITIONS_JSON_FILE = os.path.join(script_dir, COMPETITIONS_JSON_FILE)

    locations_data = load_locations_data()
    html = fetch_competitions_html()
    if html:
        global locations_competitions
        locations_competitions, all_locations = parse_competitions(html, locations_data)
        final_competitions = list(locations_competitions.values())

        save_competitions_json(final_competitions)
        update_locations_csv(all_locations, locations_data, locations_competitions)


if __name__ == "__main__":
    main()
