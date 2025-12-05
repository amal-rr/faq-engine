#!/usr/bin/env python3
"""
Script to analyze Gong transcripts and extract Q&A patterns
"""
import json
import re
from collections import defaultdict
from typing import List, Dict, Tuple

TRANSCRIPT_FILE = "/Users/amalpaul/gong_transcripts.json"


def load_transcripts():
    """Load transcripts from JSON file"""
    with open(TRANSCRIPT_FILE, 'r') as f:
        return json.load(f)


def extract_text_from_segment(segment):
    """Extract all text from a transcript segment"""
    sentences = segment.get("sentences", [])
    return " ".join([s.get("text", "") for s in sentences])


def is_question(text):
    """Determine if text is a question"""
    text = text.strip()

    # Check if ends with question mark
    if text.endswith("?"):
        return True

    # Check for question words at the start
    question_words = ["what", "when", "where", "who", "why", "how", "can", "could", "would", "should", "is", "are", "do", "does", "did"]
    first_word = text.split()[0].lower() if text.split() else ""

    if first_word in question_words:
        return True

    return False


def extract_qa_pairs(transcript_data):
    """Extract question and answer pairs from a transcript"""
    qa_pairs = []
    transcript = transcript_data.get("transcript", [])

    for i, segment in enumerate(transcript):
        text = extract_text_from_segment(segment)

        if is_question(text):
            # Get the question
            question = text.strip()

            # Get the answer (next segment or next few segments)
            answer_parts = []
            for j in range(i + 1, min(i + 4, len(transcript))):
                answer_segment = transcript[j]
                answer_text = extract_text_from_segment(answer_segment)

                # Stop if we hit another question
                if is_question(answer_text):
                    break

                if answer_text.strip():
                    answer_parts.append(answer_text.strip())

            answer = " ".join(answer_parts) if answer_parts else "No answer captured"

            if len(question) > 10:  # Filter out very short questions
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "call_title": transcript_data.get("title", "Unknown")
                })

    return qa_pairs


def normalize_question(question):
    """Normalize question for grouping similar questions"""
    # Remove names and specific details
    normalized = question.lower()

    # Remove common filler words
    fillers = ["um", "uh", "like", "you know", "i mean"]
    for filler in fillers:
        normalized = normalized.replace(filler, "")

    # Remove extra whitespace
    normalized = " ".join(normalized.split())

    return normalized


def group_similar_questions(all_qa_pairs):
    """Group similar questions together"""
    # Simple keyword-based grouping
    grouped = defaultdict(list)

    keywords = {
        "pricing": ["price", "cost", "pricing", "expensive", "budget", "fee"],
        "integration": ["integrate", "integration", "api", "connect", "sync"],
        "features": ["feature", "functionality", "can it", "does it", "able to"],
        "implementation": ["implement", "setup", "onboard", "start", "deploy"],
        "support": ["support", "help", "assist", "training"],
        "reporting": ["report", "dashboard", "analytics", "data", "metrics"],
        "customization": ["custom", "configure", "tailor", "personalize"],
        "mobile": ["mobile", "app", "phone", "tablet"],
        "security": ["security", "secure", "encryption", "compliance"],
        "timeline": ["how long", "timeline", "when", "time frame"],
        "users": ["user", "users", "team", "people"],
        "comparison": ["compare", "difference", "versus", "vs", "better than"],
    }

    for qa in all_qa_pairs:
        question_lower = qa["question"].lower()
        categorized = False

        for category, terms in keywords.items():
            if any(term in question_lower for term in terms):
                grouped[category].append(qa)
                categorized = True
                break

        if not categorized:
            grouped["other"].append(qa)

    return grouped


def main():
    """Main execution function"""
    print("=" * 80)
    print("Gong Q&A Analyzer")
    print("=" * 80)
    print()

    # Load transcripts
    print("Loading transcripts...")
    transcripts = load_transcripts()
    print(f"Loaded {len(transcripts)} transcripts")
    print()

    # Extract Q&A pairs from all transcripts
    print("Extracting questions and answers...")
    all_qa_pairs = []

    for transcript in transcripts:
        title = transcript.get("title", "Unknown")
        print(f"  Processing: {title}")
        qa_pairs = extract_qa_pairs(transcript)
        all_qa_pairs.extend(qa_pairs)
        print(f"    Found {len(qa_pairs)} Q&A pairs")

    print()
    print(f"Total Q&A pairs extracted: {len(all_qa_pairs)}")
    print()

    # Group similar questions
    print("Grouping similar questions by topic...")
    grouped_qa = group_similar_questions(all_qa_pairs)
    print()

    # Display results
    print("=" * 80)
    print("COMMON QUESTIONS BY CATEGORY")
    print("=" * 80)
    print()

    # Sort categories by number of questions
    sorted_categories = sorted(grouped_qa.items(), key=lambda x: len(x[1]), reverse=True)

    for category, qa_list in sorted_categories:
        if len(qa_list) > 0:
            print(f"\n{'=' * 80}")
            print(f"CATEGORY: {category.upper()} ({len(qa_list)} questions)")
            print('=' * 80)

            # Show up to 10 questions per category
            for i, qa in enumerate(qa_list[:10], 1):
                print(f"\n{i}. Q: {qa['question']}")
                print(f"   A: {qa['answer'][:300]}{'...' if len(qa['answer']) > 300 else ''}")
                print(f"   [From: {qa['call_title']}]")

    # Save to JSON for further analysis
    output_file = "/Users/amalpaul/gong_qa_analysis.json"
    with open(output_file, 'w') as f:
        json.dump({
            "total_qa_pairs": len(all_qa_pairs),
            "categories": {cat: len(qas) for cat, qas in grouped_qa.items()},
            "grouped_qa": {cat: qas for cat, qas in grouped_qa.items()}
        }, f, indent=2)

    print(f"\n\n{'=' * 80}")
    print(f"Full analysis saved to: {output_file}")
    print('=' * 80)


if __name__ == "__main__":
    main()
