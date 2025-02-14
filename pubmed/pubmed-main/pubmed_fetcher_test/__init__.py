import requests
import xml.etree.ElementTree as ET
import pandas as pd
from typing import List, Dict, Tuple
import argparse
import string
import logging

# Base URLs for PubMed API
BASEURL_SRCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
BASEURL_FTCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

def mkquery(base_url: str, params: Dict[str, str]) -> str:
    """Construct a query URL."""
    query = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{base_url}?{query}"

def getXmlFromURL(base_url: str, params: Dict[str, str]) -> ET.Element:
    """Fetch XML data from PubMed API."""
    response = requests.get(mkquery(base_url, params))
    response.raise_for_status()
    return ET.fromstring(response.text)

def fetch_paper_ids(query: str, max_results: int = 100) -> Tuple[List[str], str, str]:
    """Fetch PubMed IDs for a given query."""
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': str(max_results),
        'usehistory': 'y'
    }
    root = getXmlFromURL(BASEURL_SRCH, params)
    ids = [id_node.text for id_node in root.findall('.//Id')]
    query_key = root.findtext('.//QueryKey')
    web_env = root.findtext('.//WebEnv')
    return ids, query_key, web_env

def fetch_paper_details(query_key: str, web_env: str, batch_size: int = 10) -> List[Dict]:
    """Fetch paper details from PubMed API."""
    params = {
        'db': 'pubmed',
        'query_key': query_key,
        'WebEnv': web_env,
        'retmax': str(batch_size),
        'retmode': 'xml'
    }
    root = getXmlFromURL(BASEURL_FTCH, params)
    papers = []

    for article in root.iter('PubmedArticle'):
        paper = {
            'PubmedID': article.findtext('.//PMID'),
            'Title': article.findtext('.//ArticleTitle'),
            'PublicationDate': article.findtext('.//PubDate/Year'),
            'Authors': [],
            'Affiliations': []
        }
        for author in article.findall('.//Author'):
            name = f"{author.findtext('ForeName', '')} {author.findtext('LastName', '')}".strip()
            affiliation = author.findtext('.//Affiliation')
            if name and affiliation:
                paper['Authors'].append(name)
                paper['Affiliations'].append(affiliation)
        papers.append(paper)
    return papers

def check_academic(affiliation: str) -> bool:
    """Determine if an affiliation is academic using set intersection."""
    academic_keywords = ["school", "university", "college", "institute", "research", "lab"]

    # Remove punctuations.
    affiliation = affiliation.translate(str.maketrans('', '', string.punctuation))

    # Convert string to list.
    affiliation = affiliation.lower().split()

    return any(keyword in academic_keywords for keyword in affiliation)


def process_papers(papers: List[Dict]) -> pd.DataFrame:
    """Process papers and categorize authors as academic or non-academic."""
    rows = []
    for paper in papers:
        non_academic_authors = []
        affiliations = []
        for author, affiliation in zip(paper['Authors'], paper['Affiliations']):
            is_academic = check_academic(affiliation)
            if not is_academic:
                non_academic_authors.append(author)
                affiliations.append(affiliation)
        rows.append({
            'PubmedID': paper['PubmedID'],
            'Title': paper['Title'],
            'Publication Date': paper['PublicationDate'],
            'Non-academic Author(s)': "; ".join(non_academic_authors),
            'Company Affiliation(s)': "; ".join(affiliations),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")

    parser.add_argument(
        'query',
        type=str,
        help="PubMed query string."
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        default=None,
        help="Filename to save the results as a CSV file. If not provided, prints output to console."
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help="Enable debug mode to print detailed execution logs."
    )

    args = parser.parse_args()

    # Set up logging
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting PubMed query...")
    try:
        # Step 1: Fetch PubMed IDs
        paper_ids, query_key, web_env = fetch_paper_ids(args.query)
        logging.info(f"Fetched {len(paper_ids)} paper IDs.")

        # Step 2: Fetch paper details
        papers = fetch_paper_details(query_key, web_env)
        logging.info(f"Fetched details for {len(papers)} papers.")

        # Step 3: Process papers to identify non-academic authors
        processed_df = process_papers(papers)
        logging.info("Processed paper details to identify non-academic authors.")

        # Step 4: Output results
        if args.file:
            processed_df.to_csv(args.file, index=False)
            logging.info(f"Results saved to {args.file}")
        else:
            print(processed_df.to_string(index=False))

    except Exception as e:
        logging.error("An error occurred while processing the PubMed query.", exc_info=True)

def fetch(query: str, max_results: int = 100, file_path: str = None, debug: bool = False) -> pd.DataFrame:
    """Fetch research papers from PubMed based on query."""
    logging_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting PubMed query...")
    try:
        # Step 1: Fetch PubMed IDs
        paper_ids, query_key, web_env = fetch_paper_ids(query, max_results)
        logging.info(f"Fetched {len(paper_ids)} paper IDs.")

        # Step 2: Fetch paper details
        papers = fetch_paper_details(query_key, web_env)
        logging.info(f"Fetched details for {len(papers)} papers.")

        # Step 3: Process papers to identify non-academic authors
        processed_df = process_papers(papers)
        logging.info("Processed paper details to identify non-academic authors.")

        # Step 4: Output results
        if file_path:
            processed_df.to_csv(file_path, index=False)
            logging.info(f"Results saved to {file_path}")

        return processed_df

    except Exception as e:
        logging.error("An error occurred while processing the PubMed query.", exc_info=True)
        return pd.DataFrame([])