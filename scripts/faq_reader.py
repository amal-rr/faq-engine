#!/usr/bin/env python3
"""
FAQ Reader - Demonstrate querying and filtering FAQ JSON data

This script shows how to read and query the FAQ JSON data,
demonstrating typical frontend use cases.
"""

import json
import sys
from pathlib import Path
from collections import Counter


class FAQReader:
    """Reader and query interface for FAQ data"""

    def __init__(self, json_file):
        self.json_file = json_file
        self.faqs = []

    def load(self):
        """Load FAQ data from JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.faqs = data.get("faqs", [])
            return True
        except FileNotFoundError:
            print(f"Error: File not found: {self.json_file}", file=sys.stderr)
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            return False

    def search(self, keyword, search_answers=True):
        """
        Search for keyword in questions and optionally answers.

        Args:
            keyword: The search term
            search_answers: If True, also search in shortAnswer and detailedAnswer

        Returns:
            List of matching FAQs
        """
        keyword_lower = keyword.lower()
        results = []

        for faq in self.faqs:
            # Always search in question
            if keyword_lower in faq.get("question", "").lower():
                results.append(faq)
                continue

            # Optionally search in answers
            if search_answers:
                if (keyword_lower in faq.get("shortAnswer", "").lower() or
                    keyword_lower in faq.get("detailedAnswer", "").lower()):
                    results.append(faq)

        return results

    def filter_by_category(self, category):
        """
        Filter FAQs by category.

        Args:
            category: The category name (case-insensitive)

        Returns:
            List of matching FAQs
        """
        category_lower = category.lower()
        return [
            faq for faq in self.faqs
            if category_lower in faq.get("category", "").lower()
        ]

    def filter_by_tag(self, tag):
        """
        Filter FAQs by tag.

        Args:
            tag: The tag to filter by (case-insensitive)

        Returns:
            List of matching FAQs
        """
        tag_lower = tag.lower()
        return [
            faq for faq in self.faqs
            if any(tag_lower == t.lower() for t in faq.get("tags", []))
        ]

    def filter_by_frequency(self, min_percentage):
        """
        Filter FAQs by minimum frequency percentage.

        Args:
            min_percentage: Minimum frequency threshold (0-100)

        Returns:
            List of FAQs with frequency >= min_percentage
        """
        return [
            faq for faq in self.faqs
            if faq.get("frequencyPercentage") is not None
            and faq.get("frequencyPercentage") >= min_percentage
        ]

    def get_categories(self):
        """Get all unique categories"""
        categories = set(faq.get("category") for faq in self.faqs)
        return sorted(categories)

    def get_all_tags(self):
        """Get all tags with counts"""
        all_tags = []
        for faq in self.faqs:
            all_tags.extend(faq.get("tags", []))
        return Counter(all_tags)

    def display_faq(self, faq, show_details=False):
        """
        Display a single FAQ in a readable format.

        Args:
            faq: The FAQ dictionary
            show_details: If True, show full detailed answer
        """
        print(f"\n{'─' * 70}")
        print(f"ID: {faq.get('id')}")
        print(f"Question: {faq.get('question')}")
        print(f"Category: {faq.get('category')} > {faq.get('subcategory')}")

        freq = faq.get('frequencyPercentage')
        if freq is not None:
            print(f"Frequency: {freq}%")

        print(f"\nShort Answer:")
        print(f"  {faq.get('shortAnswer')}")

        if show_details:
            print(f"\nDetailed Answer:")
            print(f"  {faq.get('detailedAnswer')}")

        tags = faq.get('tags', [])
        if tags:
            print(f"\nTags: {', '.join(tags)}")

        internal_links = faq.get('internalLinks', [])
        if internal_links:
            print(f"\nInternal Links:")
            for link in internal_links:
                print(f"  • {link}")

        external_links = faq.get('externalLinks', [])
        if external_links:
            print(f"\nExternal Links:")
            for link in external_links:
                print(f"  • {link}")

    def display_summary(self):
        """Display summary statistics"""
        print("=" * 70)
        print("FAQ DATA SUMMARY")
        print("=" * 70)
        print(f"\nTotal FAQs: {len(self.faqs)}")

        # Category breakdown
        categories = Counter(faq.get("category") for faq in self.faqs)
        print(f"\nCategories ({len(categories)}):")
        for category, count in sorted(categories.items()):
            print(f"  • {category}: {count} FAQs")

        # Frequency stats
        frequencies = [
            faq.get("frequencyPercentage")
            for faq in self.faqs
            if faq.get("frequencyPercentage") is not None
        ]
        if frequencies:
            avg = sum(frequencies) / len(frequencies)
            print(f"\nFrequency Statistics:")
            print(f"  • Average: {avg:.1f}%")
            print(f"  • Range: {min(frequencies)}% - {max(frequencies)}%")
            print(f"  • High frequency (≥75%): {sum(1 for f in frequencies if f >= 75)} FAQs")

        # Tag stats
        tag_counts = self.get_all_tags()
        print(f"\nTop 10 Tags:")
        for tag, count in tag_counts.most_common(10):
            print(f"  • {tag}: {count}")


def run_examples(reader):
    """Run example queries to demonstrate functionality"""
    print("\n" + "=" * 70)
    print("EXAMPLE QUERIES")
    print("=" * 70)

    # Example 1: Search for a keyword
    print("\n📍 Example 1: Search for 'QuickBooks'")
    results = reader.search("QuickBooks")
    print(f"Found {len(results)} results:")
    for faq in results[:3]:  # Show first 3
        print(f"  • [{faq['id']}] {faq['question']}")
    if len(results) > 3:
        print(f"  ... and {len(results) - 3} more")

    # Example 2: Filter by category
    print("\n📍 Example 2: Filter by 'PRICING' category")
    results = reader.filter_by_category("PRICING")
    print(f"Found {len(results)} results:")
    for faq in results[:3]:
        print(f"  • [{faq['id']}] {faq['question']}")
    if len(results) > 3:
        print(f"  ... and {len(results) - 3} more")

    # Example 3: Filter by tag
    print("\n📍 Example 3: Filter by 'mobile app' tag")
    results = reader.filter_by_tag("mobile app")
    print(f"Found {len(results)} results:")
    for faq in results[:3]:
        print(f"  • [{faq['id']}] {faq['question']}")
    if len(results) > 3:
        print(f"  ... and {len(results) - 3} more")

    # Example 4: High frequency FAQs
    print("\n📍 Example 4: Most frequently asked (≥75%)")
    results = reader.filter_by_frequency(75)
    print(f"Found {len(results)} high-frequency FAQs:")
    for faq in sorted(results, key=lambda x: x.get('frequencyPercentage', 0), reverse=True)[:5]:
        freq = faq.get('frequencyPercentage', 0)
        print(f"  • [{faq['id']}] ({freq}%) {faq['question']}")

    # Example 5: Show one detailed FAQ
    print("\n📍 Example 5: Detailed view of FAQ #1")
    if reader.faqs:
        reader.display_faq(reader.faqs[0], show_details=False)


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    json_file = script_dir / "faq_data.json"

    reader = FAQReader(json_file)

    if not reader.load():
        sys.exit(1)

    print(f"Loaded {len(reader.faqs)} FAQs from {json_file}")

    # Display summary
    reader.display_summary()

    # Run example queries
    run_examples(reader)

    print("\n" + "=" * 70)
    print("✓ FAQ Reader demonstration complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
