class Movie:
    """
    A class representing a movie with relevant details.

    Attributes:
        title (str): The title of the movie.
        poster_url (str): The URL of the movie's poster image.
        overview (str): A short description or summary of the movie.
        vote_average (float or str): The IMDb rating of the movie.
        release_date (str): The release date of the movie.
        movie_id (str): The unique IMDb ID of the movie.
    """
    def __init__(self, title, poster_url, overview, vote_average, release_date, movie_id):
        self.title = title
        self.poster_url = poster_url
        self.overview = overview
        self.vote_average = vote_average
        self.release_date = release_date
        self.movie_id = movie_id

    def __repr__(self):
        return f"Movie({self.title}, IMDb ID: {self.movie_id})"