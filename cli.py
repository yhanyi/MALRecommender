import argparse
import pickle
import os
from scraper import Scraper
from recommender import Recommender
import pandas as pd


def load_or_scrape_data(force_scrape=False):
    cache_file = "data.pkl"

    if not force_scrape and os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    scraper = Scraper()
    anime_df = scraper.scrape_top_anime(num_pages=4)
    manga_df = scraper.scrape_top_manga(num_pages=4)

    df = pd.concat([anime_df, manga_df], ignore_index=True)
    df.to_csv("data.csv", index=False)

    with open(cache_file, "wb") as f:
        pickle.dump(df, f)

    return df


def main():
    parser = argparse.ArgumentParser(description="MAL Recommender")
    parser.add_argument(
        "--refresh", action="store_true", help="Force refresh cache data"
    )
    args = parser.parse_args()

    print("Loading data...")
    df = load_or_scrape_data(force_scrape=args.refresh)
    recommender = Recommender(df)

    while True:
        print("\nDescribe what kind of anime/manga you're looking for:")
        print("(e.g., 'action adventure with strong female lead' or 'q' to quit)")

        query = input("> ").strip().lower()

        if query in ["q", "quit", "exit"]:
            break

        media_type = None
        if query.find("anime") != -1 and query.find("manga") != -1:
            media_type = None
        elif query.find("anime") != -1:
            media_type = "anime"
        elif query.find("manga") != -1:
            media_type = "manga"

        recommendations = recommender.get_recommendations(
            query, media_type, n_recommendations=5
        )

        print("\nRecommendations:")
        for _, row in recommendations.iterrows():
            print(f"\nTitle: {row['title']}")
            print(f"Genres: {', '.join(row['genres'])}")
            print(f"Similarity Score: {row['similarity_score']:.2f}")
            print(f"URL: {row['url']}")


if __name__ == "__main__":
    main()
