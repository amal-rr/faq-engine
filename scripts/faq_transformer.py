#!/usr/bin/env python3
"""
FAQ Transformer - Convert FAQ text file to structured JSON format

This script parses the faq_data.txt file and converts it into a structured
JSON format suitable for a frontend search/filter application.
"""

import json
import re
import sys
from pathlib import Path


def extract_field(text, field_name, multiline=False):
    """
    Extract a field value from the FAQ text.

    Args:
        text: The text to search in
        field_name: The field name to look for (e.g., "FAQ Question:")
        multiline: If True, captures until the next field marker

    Returns:
        Extracted text or empty string if not found
    """
    if multiline:
        # Match from field name to next field or section end
        pattern = rf'{re.escape(field_name)}\s*\n(.*?)(?=\n\n[A-Z][a-z]+:|$)'
        match = re.search(pattern, text, re.DOTALL)
    else:
        # Single line or paragraph
        pattern = rf'{re.escape(field_name)}\s*\n\s*(.*?)(?=\n\n|\n[A-Z]|\Z)'
        match = re.search(pattern, text, re.DOTALL)

    if match:
        value = match.group(1).strip()
        # Clean up extra whitespace while preserving paragraph breaks
        value = re.sub(r'\n\s+', ' ', value)
        value = re.sub(r'\s+', ' ', value)
        return value
    return ""


def extract_percentage(text):
    """
    Extract percentage from frequency text like "Asked in 6 out of 8 calls (75% frequency)"

    Returns:
        Integer percentage or None if not found
    """
    match = re.search(r'(\d+)%', text)
    if match:
        return int(match.group(1))
    return None


def parse_links(text):
    """
    Parse comma-separated links into array, filtering out empty/placeholder entries.

    Returns:
        List of link strings
    """
    if not text or "(Internal-only, no public link)" in text:
        return []

    # Split by comma and clean up
    links = [link.strip() for link in text.split(',')]
    # Filter out empty strings
    links = [link for link in links if link]
    return links


def parse_tags(text):
    """
    Parse comma-separated tags into array.

    Returns:
        List of tag strings
    """
    if not text:
        return []

    # Split by comma and clean up
    tags = [tag.strip() for tag in text.split(',')]
    # Filter out empty strings
    tags = [tag for tag in tags if tag]
    return tags


def is_category_header(line):
    """Check if a line is a category header (preceded by ===)"""
    return line.strip() and not line.startswith('=') and line.isupper()


def should_skip_section(category_name):
    """Determine if a section should be skipped (not an FAQ category)"""
    skip_sections = [
        'TABLE OF CONTENTS',
        'QUICK REFERENCE',
        'DOCUMENT INFORMATION',
        'ROSE ROCKET - CONSOLIDATED PROSPECT FAQ'
    ]
    return any(skip in category_name for skip in skip_sections)


def parse_faq_entry(entry_text, current_category, faq_id):
    """
    Parse a single FAQ entry into a dictionary.

    Args:
        entry_text: The text of one FAQ entry
        current_category: The current section category
        faq_id: Sequential ID for this FAQ

    Returns:
        Dictionary with FAQ data or None if parsing fails
    """
    # Extract all fields
    question = extract_field(entry_text, "FAQ Question:")
    short_answer = extract_field(entry_text, "Short Answer (30 Seconds):")
    detailed_answer = extract_field(entry_text, "Detailed Talk Track:")
    subcategory = extract_field(entry_text, "Category:")
    tags_text = extract_field(entry_text, "Tags:")
    volume_text = extract_field(entry_text, "Volume (from Gong):")
    last_updated = extract_field(entry_text, "Last Updated:")
    internal_links_text = extract_field(entry_text, "Internal Links:")
    external_links_text = extract_field(entry_text, "External Links:")

    # Skip if no question found (likely not a valid FAQ entry)
    if not question:
        return None

    # Parse complex fields
    tags = parse_tags(tags_text)
    frequency = extract_percentage(volume_text)
    internal_links = parse_links(internal_links_text)
    external_links = parse_links(external_links_text)

    return {
        "id": faq_id,
        "question": question,
        "shortAnswer": short_answer,
        "detailedAnswer": detailed_answer,
        "category": current_category,
        "subcategory": subcategory,
        "tags": tags,
        "frequencyPercentage": frequency,
        "lastUpdated": last_updated,
        "internalLinks": internal_links,
        "externalLinks": external_links
    }


def transform_faq_file(input_file, output_file):
    """
    Main transformation function.

    Args:
        input_file: Path to faq_data.txt
        output_file: Path to output faq_data.json
    """
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"Read {len(content)} characters from {input_file}")

        faqs = []
        current_category = ""
        faq_id = 1

        # Split by category headers (=== lines followed by centered text followed by ===)
        # This regex captures the category name and everything after it until the next category
        category_pattern = r'={80,}\n\s*([A-Z\s&/]+?)\s*\n={80,}'

        # Find all category headers
        category_matches = list(re.finditer(category_pattern, content))

        for i, match in enumerate(category_matches):
            category_name = match.group(1).strip()

            # Skip non-FAQ sections
            if should_skip_section(category_name):
                print(f"Skipping section: {category_name}")
                continue

            current_category = category_name
            print(f"Processing category: {current_category}")

            # Get the content for this category (from end of header to start of next category or end)
            section_start = match.end()
            section_end = category_matches[i + 1].start() if i + 1 < len(category_matches) else len(content)
            section_content = content[section_start:section_end]

            # Split this section's FAQs by --- delimiter
            faq_entries = re.split(r'\n-{70,}\n', section_content)

            for entry in faq_entries:
                entry = entry.strip()
                if not entry:
                    continue

                # Skip if doesn't contain "FAQ Question:"
                if "FAQ Question:" not in entry:
                    continue

                # Parse the FAQ entry
                faq_data = parse_faq_entry(entry, current_category, faq_id)

                if faq_data:
                    faqs.append(faq_data)
                    print(f"  Parsed FAQ {faq_id}: {faq_data['question'][:60]}...")
                    faq_id += 1

        # Create output structure
        output_data = {
            "faqs": faqs
        }

        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Successfully transformed {len(faqs)} FAQs")
        print(f"✓ Output written to {output_file}")

        return len(faqs)

    except FileNotFoundError:
        print(f"Error: Could not find input file: {input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during transformation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point"""
    # Set up file paths
    script_dir = Path(__file__).parent
    input_file = script_dir / "faq_data.txt"
    output_file = script_dir / "faq_data.json"

    print("=" * 60)
    print("FAQ Transformer")
    print("=" * 60)
    print()

    # Run transformation
    num_faqs = transform_faq_file(input_file, output_file)

    print()
    print("=" * 60)
    print(f"Transformation complete: {num_faqs} FAQs processed")
    print("=" * 60)


if __name__ == "__main__":
    main()
