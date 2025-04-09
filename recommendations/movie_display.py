class MovieDisplay:
    """
    A class to generate HTML for displaying a list of movie recommendations.

    Attributes:
        movies (list): A list of Movie objects containing movie details.

    """
    def __init__(self, movies):
        self.movies = movies

    def render_html(self):
        """
            Generates HTML for displaying movie recommendations in a grid format.

            Returns:
                str: A string containing the HTML representation of the movie cards.
        """
        html = ""
        for movie in self.movies:
            html += f"""
            <div class="col-md-3 col-sm-6 movie-card">
              <div class="card">
                <a href="/recommendations/movie/{movie.movie_id}/">
                  <img class="card-img-top" src="{movie.poster_url}" alt="{movie.title}">
                </a>
                <div class="card-body">
                  <h5 class="card-title">
                    <a href="/recommendations/movie/{movie.movie_id}/" style="text-decoration:none; color:inherit;">
                      {movie.title}
                    </a>
                  </h5>
                  <p class="card-text">{movie.overview[:100]}...</p>
                  <p class="card-text">
                      <small class="text-muted">
                        IMDB Rating: {movie.vote_average} | Released: {movie.release_date.strftime("%Y-%m-%d") if hasattr(movie.release_date, 'strftime') else movie.release_date}
                      </small>
                    </p>
                </div>
              </div>
            </div>
            """
        return html