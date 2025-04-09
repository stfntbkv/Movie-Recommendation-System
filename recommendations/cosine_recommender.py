import difflib
import pickle
import pandas as pd


class CosineRecommender:
    """
    A recommendation system that suggests similar movies based on cosine similarity.

    Attributes:
        movies_tmdb (DataFrame): A DataFrame containing movie metadata, including IMDb IDs and titles.
        similarity (numpy array): A precomputed cosine similarity matrix for movie recommendations.
    """

    def __init__(self, movies_pkl_path, similarity_path):

        self.movies_tmdb = pd.read_pickle(movies_pkl_path)

        self.movies_tmdb['imdb_id'] = self.movies_tmdb['imdb_id'].astype(str).str.strip()

        with open(similarity_path, 'rb') as f:
            self.similarity = pickle.load(f)

    def get_recommendations(self, movie_name, number_of_recommendations=12):

        """
        Recommend top similar movies based on the provided movie name using cosine similarity.

        Parameters:
            movie_name (str): The title of the movie to find similar recommendations for.
            number_of_recommendations (int): The number of recommendations to return.

        Returns:
            recommendations (list of str): A list of recommended movie titles.
        """

        list_of_all_titles = self.movies_tmdb['title'].tolist()

        find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
        if not find_close_match:
            return []

        close_match = find_close_match[0]

        index_of_the_movie = self.movies_tmdb[self.movies_tmdb.title == close_match].index.values[0]
        title_of_the_movie = self.movies_tmdb[self.movies_tmdb.title == close_match]['title'].values[0]

        similarity_score = list(enumerate(self.similarity[index_of_the_movie]))

        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        recommendations = []
        i = 1
        for movie in sorted_similar_movies:

            index = movie[0]

            title_from_index = self.movies_tmdb[self.movies_tmdb.index == index]['title'].values[0]
            if title_from_index != title_of_the_movie:
                if i <= number_of_recommendations:
                    recommendations.append(title_from_index)
                    i += 1
            if i > number_of_recommendations:
                break

        return recommendations

    def get_recommendations_by_id(self, movie_id, number_of_recommendations=12):
        """
        Recommend top similar movies based on the provided movie ID using cosine similarity.
        This method uses the same logic as get_recommendations but skips the difflib matching.

        Parameters:
            movie_id (str): The unique movie ID (imdb_id) to find recommendations for.
            number_of_recommendations (int): The number of recommendations to return.

        Returns:
            recommendations (list of str): A list of recommended movie titles.
        """
        # Ensure the movie_id is a clean string
        movie_id = str(movie_id).strip()
        # Look up the movie row by its imdb_id.
        movie_row = self.movies_tmdb[self.movies_tmdb['imdb_id'] == movie_id]
        if movie_row.empty:
            print("Movie ID not found:", movie_id)
            return []

        index_of_the_movie = movie_row.index.values[0]
        title_of_the_movie = movie_row.iloc[0]['title']

        similarity_score = list(enumerate(self.similarity[index_of_the_movie]))

        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        recommendations = []
        i = 1
        for movie in sorted_similar_movies:
            idx = movie[0]
            title_from_index = self.movies_tmdb.loc[idx, 'title']
            # Skip the movie itself.
            if title_from_index != title_of_the_movie:
                if i <= number_of_recommendations:
                    recommendations.append(title_from_index)
                    i += 1
                else:
                    break

        return recommendations
