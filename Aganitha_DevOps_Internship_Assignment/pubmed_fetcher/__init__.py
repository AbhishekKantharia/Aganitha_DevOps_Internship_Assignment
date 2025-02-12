"""
PubMed Fetcher Module

This package provides functionality to fetch research papers from PubMed
based on a user query, filtering results based on non-academic (pharmaceutical/biotech)
author affiliations.

Modules:
- fetch: Handles fetching and filtering PubMed research papers.
- utils: Contains utility functions for processing data.

Author: Abhishek Kantharia
License: MIT
"""

from .fetch import fetch_papers
from .utils import save_to_csv, extract_non_academic_authors

__all__ = ["fetch_papers", "save_to_csv", "extract_non_academic_authors"]

__version__ = "0.1.0"