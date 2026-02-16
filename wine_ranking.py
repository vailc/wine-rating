#!/usr/bin/env python3
"""Wine ranking program: add ratings (0–10, one decimal) and view past ratings."""

import json
import re
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "ratings.json"


def load_ratings():
    """Load ratings from JSON file. Returns list of dicts."""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ratings(ratings):
    """Save ratings to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ratings, f, indent=2)


def parse_rating(text):
    """
    Parse rating string. Must be 0–10 with at most one decimal place.
    Returns float or None if invalid.
    """
    text = (text or "").strip()
    if not text:
        return None
    # Allow 0–10 with optional one decimal: e.g. 7, 7.5, 10, 10.0
    if not re.match(r"^(10(\.0)?|\d(\.\d)?)$", text):
        return None
    try:
        value = float(text)
        if 0 <= value <= 10:
            return round(value, 1)
    except ValueError:
        pass
    return None


def add_rating():
    """Prompt for wine name and rating, then append to storage."""
    name = input("Wine name: ").strip()
    if not name:
        print("Wine name cannot be empty.")
        return
    while True:
        raw = input("Rating (0–10, one decimal e.g. 7.5): ").strip()
        rating = parse_rating(raw)
        if rating is not None:
            break
        print("Invalid. Use a number from 0 to 10 with at most one decimal (e.g. 8.5).")
    ratings = load_ratings()
    entry = {
        "wine": name,
        "rating": rating,
        "date": datetime.now().isoformat(),
    }
    ratings.append(entry)
    save_ratings(ratings)
    print(f"Added: {name} — {rating}/10")


def _rating_sort_key(r):
    """Sort by rating descending (best first), then by date ascending as tiebreaker."""
    return (-r["rating"], r.get("date", ""))


def view_ratings():
    """Print all stored ratings, sorted by rating (best first)."""
    ratings = load_ratings()
    if not ratings:
        print("No ratings yet. Add one from the menu.")
        return
    sorted_ratings = sorted(ratings, key=_rating_sort_key)
    print("\n--- Your wine ratings (best first) ---")
    for i, r in enumerate(sorted_ratings, 1):
        date_str = r.get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass
        print(f"  {i}. {r['wine']} — {r['rating']}/10  ({date_str})")
    print()


def delete_rating():
    """Show ratings (sorted), prompt for number to delete, then remove it."""
    ratings = load_ratings()
    if not ratings:
        print("No ratings yet. Nothing to delete.")
        return
    # Same order as view: by rating descending, then date
    sorted_indices = sorted(
        range(len(ratings)), key=lambda i: _rating_sort_key(ratings[i])
    )
    print("\n--- Your wine ratings (best first) ---")
    for display_num, real_i in enumerate(sorted_indices, 1):
        r = ratings[real_i]
        date_str = r.get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass
        print(f"  {display_num}. {r['wine']} — {r['rating']}/10  ({date_str})")
    print()
    raw = input(f"Number to delete (1–{len(ratings)}), or Enter to cancel: ").strip()
    if not raw:
        print("Cancelled.")
        return
    try:
        display_num = int(raw)
        if 1 <= display_num <= len(ratings):
            real_i = sorted_indices[display_num - 1]
            removed = ratings.pop(real_i)
            save_ratings(ratings)
            print(f"Deleted: {removed['wine']} — {removed['rating']}/10")
        else:
            print(f"Please enter a number between 1 and {len(ratings)}.")
    except ValueError:
        print("Please enter a valid number.")


def main():
    print("Wine Ranking")
    print("------------")
    while True:
        print("1. Add a rating")
        print("2. View all ratings")
        print("3. Delete a rating")
        print("4. Quit")
        choice = input("Choice (1–4): ").strip()
        if choice == "1":
            add_rating()
        elif choice == "2":
            view_ratings()
        elif choice == "3":
            delete_rating()
        elif choice == "4":
            print("Bye.")
            break
        else:
            print("Please enter 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()
