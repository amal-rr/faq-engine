#!/usr/bin/env python3
"""
Script to retrieve Gong call transcripts
"""
import requests
import json
import time
from typing import List, Dict

# Gong API credentials
ACCESS_KEY = "O3QT4JKFSNVWTEF5T3ML4PQ42U2GFLDJ"
ACCESS_SECRET = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwNzk2OTY3OTYsImFjY2Vzc0tleSI6Ik8zUVQ0SktGU05WV1RFRjVUM01MNFBRNDJVMkdGTERKIn0.7iFQpG9HcDw7Gz2sEJXuXW88CDPJDBZpckd06IWbAKw"

# API Base URL
BASE_URL = "https://api.gong.io/v2"

# Call IDs from October 2025 demos
CALL_IDS = [
    "64685239883419447",
    "7941236985640863920",
    "5436582103101034881",
    "492063216715801682",
    "4711364303897706231",
    "5181010218645460550",
    "3964851840337081597",
    "2895301550022515029",
    "2791895597349915069",
    "8895013954574880145",
    "1019180193676783947",
    "7740734105060202594",
    "7415156089038918418"
]

CALL_TITLES = [
    "Rose Rocket Demo (Oct 1)",
    "Adam & Karandeep | Rose Rocket Demo (Oct 2)",
    "Gabriel & Karandeep | Rose Rocket Demo (Oct 3)",
    "Joe & KP | Rose Rocket Demo (Oct 3)",
    "Rose Rocket Demo (Oct 3)",
    "Kanwal & Karandeep | Rose Rocket Demo (Oct 7)",
    "Rose Rocket Demo (Oct 7)",
    "Phil & Karandeep | Rose Rocket Demo (Oct 7)",
    "Milos & Karandeep | Rose Rocket Demo (Oct 8)",
    "Rose Rocket Demo (Oct 8)",
    "Matt/Nicolas Rose Rocket Demo (Oct 8)",
    "Diane & Colin | Rose Rocket Demo (Oct 9)",
    "Jeff / Nicolas Rose Rocket Demo 2.0 (Oct 9)"
]


def get_transcript(call_id: str) -> Dict:
    """Get transcript for a specific call ID"""
    url = f"{BASE_URL}/calls/transcript"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "filter": {
            "callIds": [call_id]
        }
    }

    response = requests.post(
        url,
        auth=(ACCESS_KEY, ACCESS_SECRET),
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching transcript for call {call_id}: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def main():
    """Main execution function"""
    print("=" * 80)
    print("Gong Transcript Retriever")
    print("=" * 80)
    print(f"Retrieving transcripts for {len(CALL_IDS)} demo calls...")
    print("=" * 80)
    print()

    all_transcripts = []
    successful = 0
    failed = 0

    for i, (call_id, title) in enumerate(zip(CALL_IDS, CALL_TITLES), 1):
        print(f"\n[{i}/{len(CALL_IDS)}] Fetching: {title}")
        print(f"    Call ID: {call_id}")

        transcript_data = get_transcript(call_id)

        if transcript_data:
            # Check if transcript exists
            call_transcripts = transcript_data.get("callTranscripts", [])
            if call_transcripts and len(call_transcripts) > 0:
                transcript = call_transcripts[0].get("transcript", [])
                if transcript:
                    print(f"    ✓ Retrieved transcript with {len(transcript)} segments")
                    all_transcripts.append({
                        "call_id": call_id,
                        "title": title,
                        "transcript": transcript
                    })
                    successful += 1
                else:
                    print(f"    ✗ No transcript content available")
                    failed += 1
            else:
                print(f"    ✗ No transcript data returned")
                failed += 1
        else:
            print(f"    ✗ Failed to retrieve transcript")
            failed += 1

        # Be respectful of API rate limits
        time.sleep(0.5)

    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Total calls: {len(CALL_IDS)}")
    print(f"Successfully retrieved: {successful}")
    print(f"Failed: {failed}")
    print("=" * 80)

    # Save transcripts to file
    if all_transcripts:
        output_file = "/Users/amalpaul/gong_transcripts.json"
        with open(output_file, 'w') as f:
            json.dump(all_transcripts, f, indent=2)
        print(f"\n✓ Transcripts saved to: {output_file}")

        # Show sample of first transcript
        if len(all_transcripts) > 0:
            print("\n" + "=" * 80)
            print("SAMPLE - First few lines from first transcript:")
            print("=" * 80)
            first_transcript = all_transcripts[0]["transcript"]
            for i, segment in enumerate(first_transcript[:5], 1):
                speaker = segment.get("speakerId", "Unknown")
                text = segment.get("text", "")
                print(f"\nSpeaker {speaker}: {text}")

    return all_transcripts


if __name__ == "__main__":
    try:
        transcripts = main()
        print(f"\n\nTotal transcripts retrieved: {len(transcripts)}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
