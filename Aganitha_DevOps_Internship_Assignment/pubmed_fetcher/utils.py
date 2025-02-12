"""
Utility Functions for PubMed Fetcher

This module provides helper functions for processing and saving fetched PubMed data.

Functions:
- extract_non_academic_authors: Identifies authors affiliated with pharmaceutical/biotech companies.
- save_to_csv: Saves the extracted paper data into a CSV file.
"""

import csv
import re
from typing import List, Dict


def extract_non_academic_authors(authors: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Identifies authors affiliated with pharmaceutical/biotech companies.

    Heuristics:
    - Excludes affiliations containing keywords like 'university', 'hospital', 'institute', 'college'.
    - Includes affiliations with keywords like 'pharma', 'biotech', 'laboratories', 'inc.', 'corp.', 'ltd.'.

    Args:
        authors (List[Dict[str, str]]): List of authors with their affiliations.

    Returns:
        List[Dict[str, str]]: Filtered list of non-academic authors with company affiliations.
    """
    academic_keywords = {"university", "hospital", "institute", "college", "research center"}
    industry_keywords = {"pharma", "biotech", "laboratories", "inc.", "corp.", "ltd."}

    non_academic_authors = []
    for author in authors:
        affiliation = author.get("affiliation", "").lower()
        if any(keyword in affiliation for keyword in industry_keywords) and not any(
            keyword in affiliation for keyword in academic_keywords
        ):
            non_academic_authors.append(author)

    return non_academic_authors


def save_to_csv(data: List[Dict[str, str]], filename: str = "output.csv") -> None:
    """
    Saves fetched paper data to a CSV file.

    Args:
        data (List[Dict[str, str]]): List of dictionaries containing paper details.
        filename (str): Name of the CSV file to save the results.
    """
    if not data:
        print("No data to save.")
        return

    fieldnames = ["PubMedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"]

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Results successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")