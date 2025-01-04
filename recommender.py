import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.tfidf = TfidfVectorizer(stop_words="english")
        self.content_matrix = None
        self.prepare_content_matrix()

    def prepare_content_matrix(self):
        def process_row(x):
            genres = x["genres"] if isinstance(x["genres"], list) else []
            synopsis = [str(x["synopsis"])] if not pd.isna(x["synopsis"]) else []

            additional = []
            if "studio" in x and isinstance(x["studio"], list):
                additional = x["studio"]
            elif "authors" in x and isinstance(x["authors"], list):
                additional = x["authors"]

            media_type = [str(x["media_type"])] if not pd.isna(x["media_type"]) else []

            return " ".join(genres + synopsis + additional + media_type)

        self.df["content"] = self.df.apply(process_row, axis=1)
        self.content_matrix = self.tfidf.fit_transform(self.df["content"])

    def get_recommendations(
        self, query: str, media_type: str = None, n_recommendations: int = 5
    ) -> pd.DataFrame:
        if media_type:
            query = f"{query} {media_type}"

        query_vector = self.tfidf.transform([query])
        similarity_scores = cosine_similarity(query_vector, self.content_matrix)

        similar_indices = similarity_scores.argsort()[0][-n_recommendations:][::-1]

        if media_type:
            filtered_df = self.df[self.df["media_type"] == media_type]
            similar_indices = [i for i in similar_indices if i < len(filtered_df)]
            recommendations = filtered_df.iloc[similar_indices]
        else:
            recommendations = self.df.iloc[similar_indices]

        base_cols = ["title", "score", "genres", "synopsis", "url", "media_type"]
        recommendations = recommendations[base_cols].copy()
        recommendations["similarity_score"] = similarity_scores[0][similar_indices]

        return recommendations
