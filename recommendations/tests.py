import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from recommendations.models import Rating


# INDEX VIEW TESTS
class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_status_code(self):
        """Ensure the index page returns 200."""
        response = self.client.get(reverse('index_view'))
        self.assertEqual(response.status_code, 200)

    def test_index_heading(self):
        """Checks for 'Movie Recommendations' heading."""
        response = self.client.get(reverse('index_view'))
        self.assertContains(response, "Movie Recommendations")

    def test_index_popular_section(self):
        """Page should have 'Popular Movies' section."""
        response = self.client.get(reverse('index_view'))
        self.assertContains(response, "Popular Movies")

    def test_index_template(self):
        """Uses 'recommendations/index.html' template."""
        response = self.client.get(reverse('index_view'))
        self.assertTemplateUsed(response, 'recommendations/index.html')

    def test_index_has_search_form(self):
        """Contains a search form with 'movie_input'."""
        response = self.client.get(reverse('index_view'))
        self.assertContains(response, 'name="movie_input"')

    def test_index_has_home_button(self):
        """Contains a 'Home' button."""
        response = self.client.get(reverse('index_view'))
        self.assertContains(response, "Home")

    def test_index_no_404(self):
        """Ensure not returning 404."""
        response = self.client.get(reverse('index_view'))
        self.assertNotEqual(response.status_code, 404)


###############################################################################
#                         RECOMMENDATION VIEW TESTS
###############################################################################
class RecommendationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_recommend_no_params(self):
        """If no params, show 'Please type a movie' or similar."""
        response = self.client.get(reverse('recommendation_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please type a movie")

    def test_recommend_with_movie_input(self):
        """Checks normal flow with a valid 'movie_input' param."""
        response = self.client.get(reverse('recommendation_view'), {'movie_input': 'Frozen', 'num_recs': 5})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Please type a movie")
        self.assertContains(response, "Recommendations for")

    def test_recommend_with_movie_id(self):
        """If 'movie_id' is given, uses get_recommendations_by_id logic."""
        response = self.client.get(reverse('recommendation_view'), {'movie_id': '12345'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommendations for")

    def test_recommend_template(self):
        """Uses 'recommendations/recommendations.html'."""
        response = self.client.get(reverse('recommendation_view'), {'movie_input': 'Frozen'})
        self.assertTemplateUsed(response, 'recommendations/recommendations.html')

    def test_recommend_invalid_num_recs(self):
        """Handles invalid 'num_recs' gracefully (e.g., defaults or no crash)."""
        response = self.client.get(reverse('recommendation_view'), {'movie_input': 'Frozen', 'num_recs': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_recommend_strip_input(self):
        """Strips whitespace from user input."""
        response = self.client.get(reverse('recommendation_view'), {'movie_input': '  Frozen  '})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommendations for")


###############################################################################
#                           AUTOCOMPLETE VIEW TESTS
###############################################################################
class AutocompleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_auto_status_code(self):
        """Autocomplete returns 200 with 'term'."""
        response = self.client.get(reverse('autocomplete_view'), {'term': 'Fro'})
        self.assertEqual(response.status_code, 200)

    def test_auto_json_structure(self):
        """Response should be valid JSON and a list."""
        response = self.client.get(reverse('autocomplete_view'), {'term': 'Frozen'})

        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list,"Autocomplete did not return valid JSON")



    def test_auto_no_term(self):
        """If no 'term', returns empty list or similar."""
        response = self.client.get(reverse('autocomplete_view'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_auto_partial_input(self):
        """Partial input returns something or empty if no match."""
        response = self.client.get(reverse('autocomplete_view'), {'term': 'Inc'})
        self.assertEqual(response.status_code, 200)

    def test_auto_item_keys(self):
        """Items should have 'label' and 'value' keys."""
        response = self.client.get(reverse('autocomplete_view'), {'term': 'Frozen'})
        data = json.loads(response.content.decode())
        #Remove the data
        if data:
            self.assertIn('label', data[0])
            self.assertIn('value', data[0])


# MOVIE DETAIL VIEW TESTS

class MovieDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_imdb_id = '12345'

    def test_detail_status_code_found(self):
        """Suppose '12345' is recognized, returns 200."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertEqual(response.status_code, 200)

    def test_detail_not_found(self):
        """Nonexistent ID returns page with 'Movie not found' message."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': 'nonexistent'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Movie not found")

    def test_detail_overview_label(self):
        """Checks for 'Overview' label in the template."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertContains(response, "Overview")

    def test_detail_imdb_rating_label(self):
        """Checks for 'IMDB Rating:' label."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertContains(response, "IMDB Rating:")

    def test_detail_template(self):
        """Uses 'recommendations/movie_detail.html'."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertTemplateUsed(response, 'recommendations/movie_detail.html')

    def test_detail_poster_img(self):
        """Contains <img> for the poster."""
        response = self.client.get(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertIn(b'<img', response.content)


###############################################################################
#                            RATING VIEW TESTS
###############################################################################
class RateMovieViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.test_imdb_id = '12345'

    def test_rate_requires_login(self):
        """If not logged in, should not be 200."""
        response = self.client.get(reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertNotEqual(response.status_code, 200)

    def test_rate_get_logged_in(self):
        """Logged in user can GET rating form."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rate This Movie")

    def test_rate_post_valid(self):
        """Submitting a valid rating results in a redirect and saves data."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}),
            data={'rating': 8}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Rating.objects.filter(user=self.user, movie_id=self.test_imdb_id, rating=8).exists())

    def test_rate_post_update(self):
        """Updating an existing rating changes the value."""
        self.client.login(username="testuser", password="testpass")
        Rating.objects.create(user=self.user, movie_id=self.test_imdb_id, rating=5)
        response = self.client.post(
            reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}),
            data={'rating': 9}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Rating.objects.filter(user=self.user, movie_id=self.test_imdb_id, rating=9).exists())
        self.assertFalse(Rating.objects.filter(user=self.user, movie_id=self.test_imdb_id, rating=5).exists())

    def test_rate_template(self):
        """Uses 'recommendations/rate_movie.html'."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}))
        self.assertTemplateUsed(response, 'recommendations/rate_movie.html')

    def test_rate_login_redirect(self):
        """Check actual redirect if not logged in."""
        response = self.client.get(reverse('rate_movie_view', kwargs={'imdb_id': '98765'}))
        self.assertIn('/login', response.url)

    def test_rate_movie_view_post_redirect_details(self):
        """
        If we provide return_to=details, after posting a valid rating,
        the view should redirect to the movie_detail_view.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}) + "?return_to=details",
            data={'rating': 8}
        )
        # We expect a 302 redirect
        self.assertEqual(response.status_code, 302)
        # Check that the redirect URL includes the movie detail route
        self.assertIn(reverse('movie_detail_view', kwargs={'imdb_id': self.test_imdb_id}), response.url)
        self.assertTrue(Rating.objects.filter(user=self.user, movie_id=self.test_imdb_id, rating=8).exists())

    def test_rate_movie_view_post_redirect_my_ratings(self):
        """
        If we provide return_to=my_ratings, after posting a valid rating,
        the view should redirect to the my_ratings_view.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse('rate_movie_view', kwargs={'imdb_id': self.test_imdb_id}) + "?return_to=my_ratings",
            data={'rating': 7}
        )
        # We expect a 302 redirect
        self.assertEqual(response.status_code, 302)
        # Check that it redirects to my_ratings_view
        self.assertIn(reverse('my_ratings_view'), response.url)
        self.assertTrue(Rating.objects.filter(user=self.user, movie_id=self.test_imdb_id, rating=7).exists())


# MY RATINGS VIEW TESTS

class MyRatingsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        Rating.objects.create(user=self.user, movie_id="12345", rating=9)

    def test_my_ratings_requires_login(self):
        """If user not logged in, can't access or is redirected."""
        response = self.client.get(reverse('my_ratings_view'))
        self.assertNotEqual(response.status_code, 200)

    def test_my_ratings_status_code_logged_in(self):
        """Logged in user can access my_ratings_view."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('my_ratings_view'))
        self.assertEqual(response.status_code, 200)

    def test_my_ratings_template(self):
        """Uses 'recommendations/my_ratings.html'."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('my_ratings_view'))
        self.assertTemplateUsed(response, 'recommendations/my_ratings.html')

    def test_my_ratings_heading(self):
        """Page shows 'My Ratings' heading."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('my_ratings_view'))
        self.assertContains(response, "My Ratings")

    def test_my_ratings_none_for_other_user(self):
        """Another user with no ratings sees 'You haven't rated any movies yet.'"""
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(reverse('my_ratings_view'))
        self.assertContains(response, "You haven't rated any movies yet.")

    def test_my_ratings_displays_something_for_testuser(self):
        """Original user sees at least 1 rating. We won't check the ID specifically."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('my_ratings_view'))
        self.assertIn(b'9', response.content)

    def test_my_ratings_logout_redirect(self):
        """If we logout and try to access my_ratings, we can't get 200."""
        self.client.login(username='testuser', password='testpass')
        self.client.logout()
        response = self.client.get(reverse('my_ratings_view'))
        self.assertNotEqual(response.status_code, 200)


class UserDisplayTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_no_user_display_when_not_logged_in(self):
        """
        If not logged in, 'Welcome, testuser!' should not appear on the page.
        """
        response = self.client.get(reverse('index_view'))  # or any page that uses the header
        self.assertNotContains(response, "Welcome, testuser!")

    def test_user_display_when_logged_in(self):
        """
        If logged in, we should see 'Welcome, testuser!' in the header.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('index_view'))
        self.assertContains(response, "Welcome, testuser!")
