from django.shortcuts import render, redirect
import difflib
from .cosine_recommender import CosineRecommender
from .movie import Movie
from .movie_display import MovieDisplay
from .models import Rating
import os
from django.http import JsonResponse
import pandas as pd

from django.contrib.auth import login
from .forms import RegistrationForm
from .forms import RatingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

APP_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))

MOVIES_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'movies_filter.pkl')

SIMILARITY_PATH = os.path.join(APP_DIR, 'ml_models', 'cosine_matrix')

cosine_recommender = CosineRecommender(MOVIES_CSV_PATH, SIMILARITY_PATH)


def recommendation_view(request):
    """
    Generates movie recommendations using CosineRecommender.

    Parameters:
        request (HttpRequest): The HTTP request containing query parameters.
            - movie_input (str, optional): Movie title entered by the user.
            - movie_id (str, optional): IMDb ID of a movie.
            - num_recs (int, optional): Number of recommendations to generate. Default is 10.

    Returns:
        HttpResponse: Rendered template with recommended movies.
    """
    movie_input = request.GET.get('movie_input')
    movie_id = request.GET.get('movie_id')
    try:
        num_recs = int(request.GET.get('num_recs', 10))
    except ValueError:
        num_recs = 10

    final_title = ""
    recommended_titles = []
    if not movie_input and not movie_id:
        rendered_html = "<p>Please type a movie to get recommendations.</p>"
        return render(request, 'recommendations/recommendations.html', {'rendered_html': rendered_html})

    if movie_id:

        recommended_titles = cosine_recommender.get_recommendations_by_id(movie_id, number_of_recommendations=num_recs)

        row = cosine_recommender.movies_tmdb[
            cosine_recommender.movies_tmdb['imdb_id'].astype(str).str.strip() == movie_id.strip()
            ]
        if not row.empty:
            final_title = row.iloc[0]['title']
        else:
            final_title = movie_input or ""
    elif movie_input:

        list_of_all_titles = [t.strip() for t in cosine_recommender.movies_tmdb['title'].tolist()]
        find_close_match = difflib.get_close_matches(movie_input.strip(), list_of_all_titles)
        if find_close_match:
            final_title = find_close_match[0]
        else:
            final_title = movie_input.strip()
        recommended_titles = cosine_recommender.get_recommendations(movie_input, number_of_recommendations=num_recs)
    else:
        recommended_titles = []

    if not recommended_titles:
        rendered_html = "<p>No similar movies found. Please try another movie.</p>"
    else:
        movies = []
        for title in recommended_titles:
            row = cosine_recommender.movies_tmdb[
                cosine_recommender.movies_tmdb['title'].str.strip().str.lower() == title.strip().lower()
                ]
            if row.empty:
                continue
            row = row.iloc[0]
            poster_path = row.get('poster_path', '')
            poster_url = (
                "https://image.tmdb.org/t/p/w500" + str(poster_path)
                if poster_path and not pd.isnull(poster_path)
                else "/static/images/default.jpg"
            )
            movie_obj = Movie(
                title=row.get('title', 'N/A'),
                poster_url=poster_url,
                overview=row.get('overview', 'No overview available.'),
                vote_average=row.get('imdb_rating', 'N/A'),
                release_date=row.get('release_date', 'N/A'),
                movie_id=row.get('imdb_id', 'N/A')
            )
            movies.append(movie_obj)
        display = MovieDisplay(movies)
        rendered_html = display.render_html()

    context = {
        'rendered_html': rendered_html,
        'movie_input': final_title,  # Use the full, matched title for display in the header.
    }
    return render(request, 'recommendations/recommendations.html', context)


def movie_detail_view(request, imdb_id):
    """
    Displays detailed information for a given movie based on its IMDb ID.

    Parameters:
        request (HttpRequest): The HTTP request containing query parameters.
        imdb_id (str): The IMDb ID of the movie.

    Returns:
        HttpResponse: Rendered template with movie details or an error message if the movie is not found.
    """

    movie_row = cosine_recommender.movies_tmdb[
        cosine_recommender.movies_tmdb['imdb_id'] == imdb_id
    ]
    if movie_row.empty:
        return render(request, 'recommendations/movie_detail.html', {'error': 'Movie not found.'})

    movie = movie_row.iloc[0]
    poster_path = movie.get('poster_path', '')
    poster_url = ("https://image.tmdb.org/t/p/w500" + str(poster_path)
                  if poster_path and not pd.isnull(poster_path)
                  else "/static/images/default.jpg")

    try:
        imdb_votes = int(float(movie.get('imdb_votes', 'N/A')))
    except (ValueError, TypeError):
        imdb_votes = 'N/A'
    try:
        runtime = int(float(movie.get('runtime', 'N/A')))
    except (ValueError, TypeError):
        runtime = 'N/A'

    spoken_languages = movie.get('spoken_languages', 'N/A')
    if isinstance(spoken_languages, list):
        spoken_languages = ", ".join(spoken_languages)
    elif isinstance(spoken_languages, str):
        spoken_languages = spoken_languages.strip("[]").replace("'", "")

    user_rating = None
    if request.user.is_authenticated:
        try:
            from .models import Rating  # ensure Rating is imported
            user_rating = Rating.objects.get(user=request.user, movie_id=imdb_id).rating
        except Rating.DoesNotExist:
            user_rating = None

    context = {
        'title': movie.get('title', 'N/A'),
        'overview': movie.get('overview', 'N/A'),
        'release_date': movie.get('release_date', 'N/A'),
        'runtime': runtime,
        'genres': movie.get('genres', 'N/A'),
        'spoken_languages': spoken_languages,
        'cast': movie.get('cast', 'N/A'),
        'director': movie.get('director', 'N/A'),
        'writers': movie.get('writers', 'N/A'),
        'imdb_rating': movie.get('imdb_rating', 'N/A'),
        'imdb_votes': imdb_votes,
        'poster_url': poster_url,
        'movie_id': imdb_id,  # Pass the movie ID for links
        'user_rating': user_rating,  # This will be None if not rated
    }

    return render(request, 'recommendations/movie_detail.html', context)


def index_view(request):
    """
    Displays the homepage with a search bar for movie recommendations at the top,
    and a section below showing a shuffled sample of 5 popular movies.

    Parameters:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered template with popular movies.
    """
    # Get the top 100 popular movies (assuming higher 'popularity' means more popular)
    top_popular = cosine_recommender.movies_tmdb.sort_values(by='popularity', ascending=False).head(100)
    # Randomly sample 5 movies from the top 100
    sample_popular = top_popular.sample(n=5)

    popular_movies = []
    for _, row in sample_popular.iterrows():
        poster_path = row.get('poster_path', '')
        if poster_path:
            poster_url = "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            poster_url = "/static/images/default.jpg"

        # Create a Movie object with key details
        movie_obj = Movie(
            title=row.get('title', 'N/A'),
            poster_url=poster_url,
            overview=row.get('overview', 'No overview available.'),
            vote_average=row.get('imdb_rating', 'N/A'),
            release_date=row.get('release_date', 'N/A'),
            movie_id=row.get('imdb_id', 'N/A')
        )
        popular_movies.append(movie_obj)

    display = MovieDisplay(popular_movies)
    rendered_html = display.render_html()

    context = {
        'rendered_html': rendered_html,
    }
    return render(request, 'recommendations/index.html', context)


def autocomplete_view(request):
    """
        Provides autocomplete suggestions for movie titles based on a user's input.

        Parameters:
            request (HttpRequest): The HTTP request containing query parameters.
                - term (str, optional): The search term entered by the user.

        Returns:
            JsonResponse: A JSON list of matching movie titles, each containing:
                - label (str): Movie title with release year.
                - value (str): IMDb ID of the movie.
                - poster_url (str): URL of the movie's poster.
    """
    query = request.GET.get('term', '')
    suggestions = []
    if query:
        matches = cosine_recommender.movies_tmdb[
            cosine_recommender.movies_tmdb['title'].str.contains(query, case=False, na=False)
        ].head(10)
        for _, row in matches.iterrows():
            title = row['title'].strip()
            release_date = row.get('release_date', '')
            # Check if release_date is a Timestamp or datetime-like object:
            if isinstance(release_date, pd.Timestamp):
                year = str(release_date.year)
            elif isinstance(release_date, str) and release_date:
                year = release_date.split("-")[0]
            else:
                year = ""
            imdb_id = str(row.get('imdb_id', '')).strip()
            poster_path = row.get('poster_path', '')
            if poster_path and not pd.isnull(poster_path):
                poster_url = "https://image.tmdb.org/t/p/w500" + str(poster_path)
            else:
                poster_url = "/static/images/default.jpg"
            label = f"{title} ({year})" if year else title
            suggestions.append({
                'label': label,
                'value': imdb_id,
                'poster_url': poster_url,
            })
    return JsonResponse(suggestions, safe=False)


def register_view(request):
    """
    Handles user registration by displaying a registration form and processing submissions.

    Parameters:
        request (HttpRequest): The HTTP request containing form data if submitted.

    Returns:
        HttpResponse: Rendered registration form template, or redirects to the homepage upon successful registration.
    """

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user immediately after registration
            return redirect('index_view')  # Redirect to homepage (or wherever you prefer)
    else:
        form = RegistrationForm()
    return render(request, 'recommendations/register.html', {'form': form})


@login_required
def rate_movie_view(request, imdb_id):
    """
    Allows a logged-in user to submit or update a rating for a movie.

    Parameters:
        request (HttpRequest): The HTTP request containing form data.
        imdb_id (str): The IMDb ID of the movie being rated.

    Returns:
        HttpResponse: Redirects to the appropriate page based on the 'return_to' parameter, or displays the rating form.
    """
    try:
        rating_instance = Rating.objects.get(user=request.user, movie_id=imdb_id)
    except Rating.DoesNotExist:
        rating_instance = None

    return_to = request.GET.get('return_to')  # e.g., "details" or "my_ratings"

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating_instance)
        if form.is_valid():
            rating_obj = form.save(commit=False)
            rating_obj.user = request.user
            rating_obj.movie_id = imdb_id
            rating_obj.save()
            messages.success(request, "Your rating has been saved.")

            # Choose the redirect based on return_to
            if return_to == "details":
                # If you want to go to the movie detail page:
                return redirect('movie_detail_view', imdb_id=imdb_id)
            elif return_to == "my_ratings":
                return redirect('my_ratings_view')
            else:
                # Fallback if no valid return_to provided
                return redirect('movie_detail_view', imdb_id=imdb_id)
        else:
            messages.error(request, "There was an error with your rating. Please try again.")
    else:
        form = RatingForm(instance=rating_instance)

    context = {
        'form': form,
        'movie_id': imdb_id,
    }
    return render(request, 'recommendations/rate_movie.html', context)


@login_required
def my_ratings_view(request):
    """
      Displays all ratings submitted by the logged-in user along with movie details.

      Parameters:
          request (HttpRequest): The HTTP request.

      Returns:
          HttpResponse: Rendered template displaying the user's rated movies.
    """

    user_ratings = Rating.objects.filter(user=request.user).order_by('-updated_at')

    rated_movies = []
    for rating in user_ratings:
        movie_id = str(rating.movie_id).strip()
        movie_row = cosine_recommender.movies_tmdb[
            cosine_recommender.movies_tmdb['imdb_id'].astype(str).str.strip() == movie_id
            ]
        if movie_row.empty:
            continue
        movie = movie_row.iloc[0]
        poster_path = movie.get('poster_path', '')
        poster_url = (
            "https://image.tmdb.org/t/p/w500" + str(poster_path)
            if poster_path and not pd.isnull(poster_path)
            else "/static/images/default.jpg"
        )

        rated_movies.append({
            'title': movie.get('title', 'N/A'),
            'poster_url': poster_url,
            'rating': rating.rating,

            'date': rating.updated_at,
            'movie_id': movie_id,
        })

    context = {
        'rated_movies': rated_movies,
    }
    return render(request, 'recommendations/my_ratings.html', context)
