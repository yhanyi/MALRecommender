# MALRecommender

A mini webscraping and recommendation system to provide anime/manga suggestions from MyAnimeList data.

### Dependencies
- `beautifulsoup4` for webscraping
- `pandas` for data manipulation
- `scikit-learn` for Term Frequency - Inverse Document Frequency (TF-IDF) vectorisation and cosine similarity
- `requests` for HTTP requests

### Quickstart

1. Preferably use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
deactivate
```

2. Install dependencies:


```bash
pip install scikit-learn requests beautifulsoup4 pandas numpy
```

3. Run CLI script:


```bash
python cli.py
```

Enter your preference according to the prompt or quit.

4. Force Data Refresh

To force a refresh of the anime data:

```bash
python cli.py --refresh
```

### Notes

Please be mindful of MAL's servers when scraping data, this scraper implements a default rate limiting of 1.5 seconds between requests.

This project/code is not written according to best practices. It was made to gain exposure to simple webscraping and data analytics workflows before I start an internship.

Thanks for checking out the project!
