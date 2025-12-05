#!/usr/bin/env python3
"""
Script to find Gong call transcripts for specific criteria
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Gong API credentials
ACCESS_KEY = "O3QT4JKFSNVWTEF5T3ML4PQ42U2GFLDJ"
ACCESS_SECRET = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwNzk2OTY3OTYsImFjY2Vzc0tleSI6Ik8zUVQ0SktGU05WV1RFRjVUM01MNFBRNDJVMkdGTERKIn0.7iFQpG9HcDw7Gz2sEJXuXW88CDPJDBZpckd06IWbAKw"

# API Base URL
BASE_URL = "https://api.gong.io/v2"

# Search criteria
PARTICIPANT_NAME = "Karandeep Pabla"
PARTICIPANT_EMAIL = "karandeep.p@roserocket.com"
CALL_SUBJECT = "Rose Rocket demo"
MONTHS_BACK = 6


def get_date_range(start_month=None, end_month=None):
    """Calculate date range for the last 6 months or specific months"""
    if start_month and end_month:
        # Use specific date range for October-November 2025
        start_date = datetime(2025, start_month, 1)
        if end_month == 11:  # November
            end_date = datetime(2025, 11, 30, 23, 59, 59)
        else:
            end_date = datetime(2025, end_month, 31, 23, 59, 59)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=MONTHS_BACK * 30)  # Approximate 6 months

    # Format as ISO 8601 with timezone (required by Gong API)
    # Format: YYYY-MM-DDTHH:MM:SS-07:00
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S-00:00")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S-00:00")

    return start_str, end_str


def get_user_id_by_email(email: str) -> str:
    """Get Gong user ID from email address"""
    url = f"{BASE_URL}/users"

    headers = {
        "Content-Type": "application/json"
    }

    print(f"Looking up user ID for {email}...")

    response = requests.get(
        url,
        auth=(ACCESS_KEY, ACCESS_SECRET),
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        users = data.get("users", [])

        for user in users:
            if user.get("emailAddress", "").lower() == email.lower():
                user_id = user.get("id")
                print(f"Found user ID: {user_id}")
                return user_id

        print(f"User not found with email: {email}")
        return None
    else:
        print(f"Error fetching users: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def fetch_calls(from_date: str, to_date: str, user_id: str = None) -> List[Dict]:
    """Fetch calls from Gong API within date range using extensive endpoint"""
    url = f"{BASE_URL}/calls/extensive"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "fromDateTime": from_date,
            "toDateTime": to_date
        }
    }

    # Add user filter if user_id is provided
    if user_id:
        payload["filter"]["primaryUserId"] = [user_id]
        print(f"Filtering calls for user ID: {user_id}")

    print(f"Fetching calls from {from_date} to {to_date}...")

    response = requests.post(
        url,
        auth=(ACCESS_KEY, ACCESS_SECRET),
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        calls = data.get("calls", [])

        # Debug: show structure of first call
        if calls and len(calls) > 0:
            print(f"\nDEBUG - Available fields in first call: {list(calls[0].keys())}")

        return calls
    else:
        print(f"Error fetching calls: {response.status_code}")
        print(f"Response: {response.text}")
        return []


def filter_calls(calls: List[Dict]) -> List[Dict]:
    """Filter calls by subject containing 'demo'"""
    matching_calls = []

    for call in calls:
        metadata = call.get("metaData", {})

        # Check if title contains "Rose Rocket" and "demo"
        call_title = metadata.get("title", "").lower()
        has_rose_rocket = "rose rocket" in call_title
        has_demo = "demo" in call_title

        if has_rose_rocket and has_demo:
            matching_calls.append(call)

    return matching_calls


def main():
    """Main execution function"""
    print("=" * 60)
    print("Gong Transcript Finder")
    print("=" * 60)
    print(f"Searching for calls with:")
    print(f"  - Participant: {PARTICIPANT_NAME}")
    print(f"  - Subject: {CALL_SUBJECT}")
    print(f"  - Time period: Last {MONTHS_BACK} months")
    print("=" * 60)
    print()

    # Get date range - October to November 2025
    from_date, to_date = get_date_range(start_month=10, end_month=11)

    # Get user ID from email
    user_id = get_user_id_by_email(PARTICIPANT_EMAIL)
    if not user_id:
        print(f"\nWarning: Could not find user ID for {PARTICIPANT_EMAIL}")
        print("Proceeding without user filter...\n")

    # Fetch calls
    calls = fetch_calls(from_date, to_date, user_id)
    print(f"Total calls fetched: {len(calls)}")
    print()

    # Show a sample of calls for debugging - focus on Rose Rocket demos
    if calls and len(calls) > 0:
        print("Searching for Rose Rocket related calls...")
        print("-" * 60)
        rose_rocket_calls = [c for c in calls if "rose rocket" in c.get('metaData', {}).get('title', '').lower()]
        print(f"Found {len(rose_rocket_calls)} calls with 'Rose Rocket' in title")

        print("\nFirst 10 Rose Rocket calls:")
        for i, call in enumerate(rose_rocket_calls[:10], 1):
            # Extract metadata
            metadata = call.get('metaData', {})
            print(f"\n{i}. Title: {metadata.get('title', 'No title')}")
            print(f"   Date: {metadata.get('started', 'Unknown')}")
            print(f"   Call ID: {metadata.get('id', 'Unknown')}")

            # Show participants
            parties = metadata.get("parties", [])
            if parties:
                print(f"   Participants ({len(parties)}):")
                for p in parties:
                    name = p.get("name", "Unknown")
                    email = p.get("emailAddress", "")
                    affiliation = p.get("affiliation", "Unknown")
                    print(f"     - {name} ({email}) - {affiliation}")
            else:
                print(f"   Participants: None found (keys: {list(metadata.keys())})")
        print("-" * 60)
        print()

    # Filter calls
    matching_calls = filter_calls(calls)

    print("=" * 60)
    print(f"RESULTS: Found {len(matching_calls)} matching calls")
    print("=" * 60)
    print()

    if matching_calls:
        print("Matching calls:")
        for i, call in enumerate(matching_calls, 1):
            metadata = call.get('metaData', {})
            print(f"\n{i}. {metadata.get('title', 'No title')}")
            print(f"   Date: {metadata.get('started', 'Unknown')}")
            print(f"   Duration: {metadata.get('duration', 0) / 1000 / 60:.1f} minutes")
            print(f"   Call ID: {metadata.get('id', 'Unknown')}")

            # Show participants
            participants = metadata.get("parties", [])
            if participants:
                print(f"   Participants:")
                for p in participants:
                    name = p.get("name", "Unknown")
                    email = p.get("emailAddress", "")
                    print(f"     - {name} ({email})")
    else:
        print("No matching calls found.")
        print("\nTroubleshooting tips:")
        print("1. Verify the participant name is spelled correctly")
        print("2. Check if the call subject matches exactly")
        print("3. Ensure calls exist within the specified date range")

    return len(matching_calls)


if __name__ == "__main__":
    try:
        count = main()
        print(f"\n\nTotal transcripts available: {count}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
