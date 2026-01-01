import json
import os


def verify_locations():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(script_dir, "competitions.json")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        locations = json.load(f)

    missing_coords = []
    missing_websites = []

    for loc in locations:
        if not loc.get("latitude") or not loc.get("longitude"):
            missing_coords.append(f"{loc['club']} - {loc['location']}")
        if not loc.get("website"):
            missing_websites.append(f"{loc['club']}")

    if missing_coords:
        print("Locations with missing coordinates:")
        for loc in sorted(list(set(missing_coords))):
            print(f"- {loc}")
    else:
        print("All locations have coordinates.")

    if missing_websites:
        print("\nClubs with missing websites (no regulation link found yet):")
        for club in sorted(list(set(missing_websites))):
            print(f"- {club}")
    else:
        print("\nAll clubs have websites.")


if __name__ == "__main__":
    verify_locations()
