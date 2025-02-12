import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import pandas as pd

NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

class PubMedFetcher:
    def __init__(self, email: str):
        """Initialize with email for API compliance."""
        self.email = email

    def search_papers(self, query: str, max_results: int = 20) -> List[str]:
        """Search PubMed and return list of PubMed IDs."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "xml",
            "retmax": max_results,
            "email": self.email,
        }
        response = requests.get(f"{NCBI_BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        return [id_elem.text for id_elem in root.findall(".//Id")]

    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict]:
        """Fetch paper details given PubMed IDs."""
        if not pubmed_ids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pubmed_ids),
            "retmode": "xml",
            "email": self.email,
        }
        response = requests.get(f"{NCBI_BASE_URL}/efetch.fcgi", params=params)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        papers = []

        for article in root.findall(".//PubmedArticle"):
            pubmed_id = article.find(".//PMID").text
            title = article.find(".//ArticleTitle").text or "N/A"
            pub_date = article.find(".//PubDate/Year")
            pub_date = pub_date.text if pub_date is not None else "Unknown"

            authors, companies, email = self.extract_authors(article)
            if companies:  # Only save if there is at least one non-academic author
                papers.append({
                    "PubMed ID": pubmed_id,
                    "Title": title,
                    "Publication Date": pub_date,
                    "Non-academic Author(s)": ", ".join(authors) if authors else "N/A",
                    "Company Affiliation(s)": ", ".join(companies),
                    "Corresponding Author Email": email or "N/A",
                })

        return papers

    def extract_authors(self, article) -> (List[str], List[str], Optional[str]):
        """Extract non-academic authors, company affiliations, and corresponding author email."""
        authors = []
        companies = []
        email = None

        for author in article.findall(".//Author"):
            name = f"{author.findtext('ForeName', '')} {author.findtext('LastName', '')}".strip()
            affiliation = author.findtext(".//AffiliationInfo/Affiliation", "")

            if self.is_non_academic(affiliation):
                authors.append(name)
                companies.append(affiliation)

            if author.find(".//ElectronicAddress") is not None:
                email = author.find(".//ElectronicAddress").text

        return authors, companies, email

    @staticmethod
    def is_non_academic(affiliation: str) -> bool:
        """Check if affiliation is from a company (not university, hospital, etc.)."""
        academic_keywords = ["university", "college", "institute", "hospital", "school"]
        return any(word in affiliation.lower() for word in ["pharma", "biotech", "corp", "inc"]) and \
               not any(word in affiliation.lower() for word in academic_keywords)

def save_to_csv(papers: List[Dict], filename: str):
    """Save fetched papers to a CSV file."""
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)