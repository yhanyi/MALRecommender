import argparse
import pickle
import os
from scraper import Scraper
from recommender import Recommender


def load_or_scrape_data(force_scrape=False):
    cache_file = "anime_data.pkl"

    if not force_scrape and os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    scraper = Scraper()
    df = scraper.scrape_top_anime(num_pages=4)

    with open(cache_file, "wb") as f:
        pickle.dump(df, f)

    return df


def main():
    parser = argparse.ArgumentParser(description="MAL Recommendation System")
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh anime data"
    )
    args = parser.parse_args()

    print("Loading anime data...")
    df = load_or_scrape_data(force_scrape=args.refresh)
    recommender = Recommender(df)

    while True:
        print("\nDescribe what kind of anime you're looking for:")
        print("(e.g., 'action adventure with strong female lead' or 'q' to quit)")

        query = input("> ").strip()

        if query.lower() in ["q", "quit", "exit"]:
            break

        recommendations = recommender.get_recommendations(query, n_recommendations=5)

        print("\nRecommended Anime:")
        for _, row in recommendations.iterrows():
            print(f"\nTitle: {row['title']}")
            print(f"Genres: {', '.join(row['genres'])}")
            print(f"Similarity Score: {row['similarity_score']:.2f}")
            print(f"URL: {row['url']}")


if __name__ == "__main__":
    main()
