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
        self.df["content"] = self.df.apply(
            lambda x: " ".join(
                x["genres"] + [x["synopsis"]] + x["studio"],
            ),
            axis=1,
        )
        self.content_matrix = self.tfidf.fit_transform(self.df["content"])

    def get_recommendations(
        self, query: str, n_recommendations: int = 5
    ) -> pd.DataFrame:
        query_vector = self.tfidf.transform([query])
        similarity_scores = cosine_similarity(query_vector, self.content_matrix)
        similar_indices = similarity_scores.argsort()[0][-n_recommendations:][::-1]
        recommendations = self.df.iloc[similar_indices][
            ["title", "score", "genres", "synopsis", "url"]
        ].copy()
        recommendations["similarity_score"] = similarity_scores[0][similar_indices]
        return recommendations
