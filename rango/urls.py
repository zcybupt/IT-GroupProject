from django.urls import path
from rango import views
app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    path('add_category/', views.add_category, name='add_category'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),

    path('movies/', views.get_movie, name='movie_detail'),
    path('movies/<int:movie_id>/', views.get_movie, name='movie_detail'),
    path('movies/<int:movie_id>/<int:page>', views.get_movie, name='movie_detail'),
    path('movies/<int:movie_id>/review', views.add_movie_review, name='add_movie_review'),
    path('movies/top/', views.get_top_movies, name='top_movies'),
    path('movies/top/<int:page>/', views.get_top_movies, name='top_movies'),
    path('movies/latest/', views.get_latest_movies, name='latest_movies'),
    path('movies/latest/<int:page>/', views.get_latest_movies, name='latest_movies'),
    path('movies/search/', views.search_movies, name='movie_search'),
    path('movies/search/<str:keyword>/', views.search_more_movies, name='movie_search'),
    path('movies/search/<str:keyword>/<int:page>/', views.search_more_movies, name='movie_search'),

    path('genres/', views.get_movies_by_genre, name='genres'),
    path('genres/<str:genre>/', views.get_movies_by_genre, name='genres'),
    path('genres/<str:genre>/<int:page>/', views.get_movies_by_genre, name='genres'),

    path('reviews/', views.get_popular_reviews, name='popular_reviews'),
    path('reviews/popular/', views.get_popular_reviews, name='popular_reviews'),
    path('reviews/popular/<int:page>', views.get_popular_reviews, name='popular_reviews'),
    path('reviews/like/', views.like_review, name='like_review'),
    path('reviews/<str:user_name>/', views.get_reviews_by_user, name='reviews'),
    path('reviews/<str:user_name>/<int:page>/', views.get_reviews_by_user, name='reviews_page'),
]