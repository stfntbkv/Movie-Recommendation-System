from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    A model representing a user profile linked to the Django User model.

    Attributes:
       user (User): A one-to-one relationship with the built-in Django User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Rating(models.Model):
    """
    A model representing a user's rating for a specific movie.

    Attributes:
        user (User): A foreign key linking the rating to a specific user.
        movie_id (str): A unique identifier for the movie being rated.
        rating (int): The numerical rating given by the user.
        created_at (datetime): Timestamp when the rating was first created.
        updated_at (datetime): Timestamp when the rating was last updated.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie_id = models.CharField(max_length=50)
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the Rating model.

        Attributes:
            unique_together (tuple): Ensures that a user can only rate a specific movie once.
        """
        unique_together = ('user', 'movie_id')

    def __str__(self):
        return f"{self.user.username} rated {self.movie_id} = {self.rating}"
