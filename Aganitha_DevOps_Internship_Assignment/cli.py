"""
Command-Line Interface for PubMed Fetcher

This script allows users to fetch research papers from PubMed using a query,
filter papers with non-academic (pharmaceutical/biotech) authors, and save results to a CSV file.

Usage:
    poetry run get-papers-list "your search query" --email your@email.com -f results.csv

Options:
    -h, --help       Show help message and exit.
    -d, --debug      Enable debug mode for detailed logs.
    -f, --file       Specify filename to save results as a CSV.
    --email          Required: Email address for PubMed API compliance.

Author: Abhishek Kantharia
Repository License: MIT License
"""

import argparse
import sys
from pubmed_fetcher.fetch import PubMedFetcher, save_to_csv

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers with non-academic authors from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("-f", "--file", type=str, help="Output CSV filename.")
    parser.add_argument("--email", type=str, required=True, help="Your email for PubMed API compliance.")

    args = parser.parse_args()

    fetcher = PubMedFetcher(email=args.email)
    
    if args.debug:
        print(f"Searching for papers using query: {args.query}")

    pubmed_ids = fetcher.search_papers(args.query)

    if args.debug:
        print(f"Found {len(pubmed_ids)} papers.")

    papers = fetcher.fetch_paper_details(pubmed_ids)

    if papers:
        if args.file:
            save_to_csv(papers, args.file)
            print(f"Results saved to {args.file}")
        else:
            for paper in papers:
                print(paper)
    else:
        print("No relevant papers found.")

if __name__ == "__main__":
    main()