from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index_view, name='index_view'),
    path('recommendations/', views.recommendation_view, name='recommendation_view'),
    path('recommendations/movie/<str:imdb_id>/', views.movie_detail_view, name='movie_detail_view'),
    path('rate/<str:imdb_id>/', views.rate_movie_view, name='rate_movie_view'),
    path('register/', views.register_view, name='register_view'),
    path('my-ratings/', views.my_ratings_view, name='my_ratings_view'),
    path('login/', auth_views.LoginView.as_view(template_name='recommendations/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('autocomplete/', views.autocomplete_view, name='autocomplete_view'),
]
