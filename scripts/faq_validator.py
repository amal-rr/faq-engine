#!/usr/bin/env python3
"""
FAQ Validator - Validate the structure and data quality of FAQ JSON

This script validates that the generated faq_data.json file has the correct
structure and high-quality data suitable for frontend consumption.
"""

import json
import sys
from pathlib import Path
from collections import Counter
import re


class FAQValidator:
    """Validator for FAQ JSON data"""

    def __init__(self, json_file):
        self.json_file = json_file
        self.data = None
        self.errors = []
        self.warnings = []

    def load_json(self):
        """Load and parse JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.json_file}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading file: {e}")
            return False

    def validate_schema(self):
        """Validate the overall JSON schema"""
        print("Validating schema...")

        # Check root structure
        if not isinstance(self.data, dict):
            self.errors.append("Root must be an object/dict")
            return

        if "faqs" not in self.data:
            self.errors.append("Root must have 'faqs' key")
            return

        if not isinstance(self.data["faqs"], list):
            self.errors.append("'faqs' must be an array/list")
            return

        # Check each FAQ entry
        required_fields = {
            "id": int,
            "question": str,
            "shortAnswer": str,
            "detailedAnswer": str,
            "category": str,
            "subcategory": str,
            "tags": list,
            "frequencyPercentage": (int, type(None)),
            "lastUpdated": str,
            "internalLinks": list,
            "externalLinks": list
        }

        for i, faq in enumerate(self.data["faqs"]):
            faq_id = faq.get("id", f"index-{i}")

            # Check all required fields exist
            for field, expected_type in required_fields.items():
                if field not in faq:
                    self.errors.append(f"FAQ {faq_id}: Missing field '{field}'")
                    continue

                value = faq[field]

                # Check type
                if isinstance(expected_type, tuple):
                    # Allow multiple types (e.g., int or None)
                    if not any(isinstance(value, t) for t in expected_type):
                        type_names = " or ".join(t.__name__ for t in expected_type)
                        self.errors.append(
                            f"FAQ {faq_id}: Field '{field}' must be {type_names}, "
                            f"got {type(value).__name__}"
                        )
                else:
                    if not isinstance(value, expected_type):
                        self.errors.append(
                            f"FAQ {faq_id}: Field '{field}' must be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )

                # Check non-empty strings
                if expected_type == str and field not in ["lastUpdated"]:
                    if not value or not value.strip():
                        self.errors.append(f"FAQ {faq_id}: Field '{field}' cannot be empty")

        print(f"  Checked {len(self.data['faqs'])} FAQ entries")

    def validate_data_quality(self):
        """Validate data quality and consistency"""
        print("Validating data quality...")

        faqs = self.data.get("faqs", [])
        if not faqs:
            return

        # Track IDs for uniqueness check
        ids = []
        categories = []

        for i, faq in enumerate(faqs):
            faq_id = faq.get("id")
            ids.append(faq_id)

            # Validate ID sequence
            expected_id = i + 1
            if faq_id != expected_id:
                self.warnings.append(
                    f"FAQ {faq_id}: ID not sequential (expected {expected_id})"
                )

            # Validate category
            category = faq.get("category", "")
            if category:
                categories.append(category)

            # Validate frequency percentage
            freq = faq.get("frequencyPercentage")
            if freq is not None:
                if not (0 <= freq <= 100):
                    self.errors.append(
                        f"FAQ {faq_id}: Frequency percentage {freq} out of range (0-100)"
                    )

            # Validate date format
            date = faq.get("lastUpdated", "")
            if date and not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                self.warnings.append(
                    f"FAQ {faq_id}: Date '{date}' doesn't match YYYY-MM-DD format"
                )

            # Validate tags
            tags = faq.get("tags", [])
            for tag in tags:
                if not isinstance(tag, str):
                    self.errors.append(f"FAQ {faq_id}: Tag must be string, got {type(tag)}")
                elif tag != tag.strip():
                    self.warnings.append(
                        f"FAQ {faq_id}: Tag '{tag}' has leading/trailing whitespace"
                    )

            # Validate link arrays
            for link_field in ["internalLinks", "externalLinks"]:
                links = faq.get(link_field, [])
                for link in links:
                    if not isinstance(link, str):
                        self.errors.append(
                            f"FAQ {faq_id}: {link_field} must contain strings"
                        )

        # Check ID uniqueness
        id_counts = Counter(ids)
        duplicates = [faq_id for faq_id, count in id_counts.items() if count > 1]
        if duplicates:
            self.errors.append(f"Duplicate IDs found: {duplicates}")

        # Check FAQ count
        total_faqs = len(faqs)
        if total_faqs < 45 or total_faqs > 60:
            self.warnings.append(
                f"FAQ count {total_faqs} is outside expected range (45-60)"
            )

        # Check category distribution
        expected_categories = {
            "PRICING & CONTRACTS",
            "INTEGRATIONS",
            "DISPATCH & OPERATIONS",
            "MOBILE APP & POD",
            "CUSTOMIZATION",
            "USER ACCESS & PERMISSIONS",
            "ONBOARDING & SETUP",
            "REPORTING & VISIBILITY",
            "DATA TRACKING & AUDIT",
            "CUSTOMER/PARTNER SHARING"
        }

        found_categories = set(categories)
        missing_categories = expected_categories - found_categories
        if missing_categories:
            self.warnings.append(
                f"Missing expected categories: {', '.join(sorted(missing_categories))}"
            )

        extra_categories = found_categories - expected_categories
        if extra_categories:
            self.warnings.append(
                f"Unexpected categories found: {', '.join(sorted(extra_categories))}"
            )

        print(f"  Validated {total_faqs} FAQs across {len(found_categories)} categories")

    def generate_statistics(self):
        """Generate and display statistics about the FAQ data"""
        print("\nStatistics:")
        print("-" * 60)

        faqs = self.data.get("faqs", [])

        # Total count
        print(f"Total FAQs: {len(faqs)}")

        # Category distribution
        categories = [faq.get("category") for faq in faqs]
        category_counts = Counter(categories)
        print(f"\nFAQs per category:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}")

        # Frequency statistics
        frequencies = [
            faq.get("frequencyPercentage")
            for faq in faqs
            if faq.get("frequencyPercentage") is not None
        ]
        if frequencies:
            avg_freq = sum(frequencies) / len(frequencies)
            print(f"\nFrequency statistics:")
            print(f"  FAQs with frequency data: {len(frequencies)}/{len(faqs)}")
            print(f"  Average frequency: {avg_freq:.1f}%")
            print(f"  Min frequency: {min(frequencies)}%")
            print(f"  Max frequency: {max(frequencies)}%")

        # Tag statistics
        all_tags = []
        for faq in faqs:
            all_tags.extend(faq.get("tags", []))
        tag_counts = Counter(all_tags)
        print(f"\nTag statistics:")
        print(f"  Total unique tags: {len(tag_counts)}")
        print(f"  Most common tags:")
        for tag, count in tag_counts.most_common(10):
            print(f"    {tag}: {count}")

    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ All validation checks passed!")

        if not self.errors:
            self.generate_statistics()

        print("\n" + "=" * 60)

    def validate(self):
        """Run all validations"""
        print("=" * 60)
        print("FAQ Validator")
        print("=" * 60)
        print()

        if not self.load_json():
            self.print_results()
            return False

        print(f"Loaded {self.json_file}")
        print()

        self.validate_schema()
        self.validate_data_quality()

        self.print_results()

        return len(self.errors) == 0


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    json_file = script_dir / "faq_data.json"

    validator = FAQValidator(json_file)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
