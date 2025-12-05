#!/usr/bin/env python3
"""
Advanced Q&A frequency analysis - find truly common questions
"""
import json
from collections import defaultdict
from difflib import SequenceMatcher

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
    if text.endswith("?"):
        return True
    question_words = ["what", "when", "where", "who", "why", "how", "can", "could", "would", "should", "is", "are", "do", "does", "did"]
    first_word = text.split()[0].lower() if text.split() else ""
    if first_word in question_words:
        return True
    return False


def normalize_question(question):
    """Normalize question for similarity matching"""
    q = question.lower().strip()

    # Remove common variations
    q = q.replace("you guys", "you")
    q = q.replace("roserocket", "rose rocket")
    q = q.replace("rose rocket", "system")

    # Remove filler words
    fillers = ["um", "uh", "like", "you know", "i mean", "kind of", "sort of"]
    for filler in fillers:
        q = q.replace(filler, "")

    # Remove extra whitespace
    q = " ".join(q.split())

    return q


def similarity(q1, q2):
    """Calculate similarity between two questions"""
    return SequenceMatcher(None, q1, q2).ratio()


def extract_all_qa_pairs(transcripts):
    """Extract all Q&A pairs from all transcripts"""
    all_qa = []

    for transcript_data in transcripts:
        transcript = transcript_data.get("transcript", [])
        call_title = transcript_data.get("title", "Unknown")

        for i, segment in enumerate(transcript):
            text = extract_text_from_segment(segment)

            if is_question(text):
                question = text.strip()

                # Get answer (next few segments)
                answer_parts = []
                for j in range(i + 1, min(i + 4, len(transcript))):
                    answer_segment = transcript[j]
                    answer_text = extract_text_from_segment(answer_segment)

                    if is_question(answer_text):
                        break

                    if answer_text.strip():
                        answer_parts.append(answer_text.strip())

                answer = " ".join(answer_parts) if answer_parts else ""

                if len(question) > 15 and len(answer) > 20:  # Filter quality
                    all_qa.append({
                        "question": question,
                        "answer": answer,
                        "normalized": normalize_question(question),
                        "call_title": call_title
                    })

    return all_qa


def cluster_similar_questions(all_qa, similarity_threshold=0.7):
    """Group similar questions together and count frequency"""
    clusters = []

    for qa in all_qa:
        # Try to find existing cluster
        found_cluster = False
        for cluster in clusters:
            # Compare with cluster representative
            if similarity(qa["normalized"], cluster["representative"]) >= similarity_threshold:
                cluster["questions"].append(qa)
                cluster["count"] += 1
                # Update best answer (longest one)
                if len(qa["answer"]) > len(cluster["best_answer"]):
                    cluster["best_answer"] = qa["answer"]
                found_cluster = True
                break

        if not found_cluster:
            # Create new cluster
            clusters.append({
                "representative": qa["normalized"],
                "original_question": qa["question"],
                "questions": [qa],
                "count": 1,
                "best_answer": qa["answer"]
            })

    return clusters


def categorize_question(question):
    """Categorize a question"""
    q_lower = question.lower()

    if any(word in q_lower for word in ["price", "cost", "fee", "dollar", "expensive", "budget", "monthly"]):
        return "PRICING"
    elif any(word in q_lower for word in ["mobile", "app", "phone", "tablet", "driver"]):
        return "MOBILE APP"
    elif any(word in q_lower for word in ["custom", "configure", "change", "modify", "edit"]):
        return "CUSTOMIZATION"
    elif any(word in q_lower for word in ["integrate", "integration", "connect", "sync", "eld", "quickbooks"]):
        return "INTEGRATION"
    elif any(word in q_lower for word in ["user", "users", "login", "access", "permission"]):
        return "USER MANAGEMENT"
    elif any(word in q_lower for word in ["track", "tracking", "eta", "live", "location"]):
        return "TRACKING"
    elif any(word in q_lower for word in ["customer", "portal", "client", "book"]):
        return "CUSTOMER PORTAL"
    elif any(word in q_lower for word in ["report", "dashboard", "analytics", "data"]):
        return "REPORTING"
    elif any(word in q_lower for word in ["implement", "onboard", "setup", "start", "training"]):
        return "IMPLEMENTATION"
    elif any(word in q_lower for word in ["signature", "photo", "pod", "proof"]):
        return "PROOF OF DELIVERY"
    else:
        return "GENERAL"


def main():
    """Main execution"""
    print("=" * 80)
    print("ADVANCED Q&A FREQUENCY ANALYSIS")
    print("=" * 80)
    print()

    # Load and extract
    print("Loading transcripts...")
    transcripts = load_transcripts()

    print("Extracting all Q&A pairs...")
    all_qa = extract_all_qa_pairs(transcripts)
    print(f"Extracted {len(all_qa)} quality Q&A pairs")
    print()

    # Cluster similar questions
    print("Clustering similar questions...")
    clusters = cluster_similar_questions(all_qa, similarity_threshold=0.65)

    # Sort by frequency
    clusters.sort(key=lambda x: x["count"], reverse=True)

    print(f"Found {len(clusters)} unique question clusters")
    print()

    # Categorize and display
    categorized = defaultdict(list)
    for cluster in clusters:
        category = categorize_question(cluster["original_question"])
        categorized[category].append(cluster)

    print("=" * 80)
    print("TOP 50 MOST FREQUENTLY ASKED QUESTIONS")
    print("=" * 80)
    print()

    rank = 1
    for cluster in clusters[:50]:
        category = categorize_question(cluster["original_question"])
        print(f"\n{rank}. [{category}] Asked {cluster['count']} times")
        print(f"   Q: {cluster['original_question']}")
        print(f"   A: {cluster['best_answer'][:250]}{'...' if len(cluster['best_answer']) > 250 else ''}")
        print(f"   ---")
        rank += 1

    # Save detailed results
    output = {
        "total_qa_pairs": len(all_qa),
        "unique_questions": len(clusters),
        "top_50": [
            {
                "rank": i + 1,
                "category": categorize_question(c["original_question"]),
                "frequency": c["count"],
                "question": c["original_question"],
                "answer": c["best_answer"],
                "appeared_in_calls": [q["call_title"] for q in c["questions"]]
            }
            for i, c in enumerate(clusters[:50])
        ]
    }

    with open("/Users/amalpaul/gong_frequency_analysis.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n\n" + "=" * 80)
    print("FREQUENCY BREAKDOWN BY CATEGORY")
    print("=" * 80)

    for category in sorted(categorized.keys()):
        questions = categorized[category]
        total_asks = sum(q["count"] for q in questions)
        print(f"\n{category}: {len(questions)} unique questions, {total_asks} total asks")

        # Show top 3 in each category
        for i, q in enumerate(questions[:3], 1):
            print(f"  {i}. ({q['count']}x) {q['original_question'][:80]}...")

    print(f"\n\nFull analysis saved to: /Users/amalpaul/gong_frequency_analysis.json")


if __name__ == "__main__":
    main()
