import os
import django
from rango.models import Genre, Movie, Review

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

django.setup()

genres = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
    'Film Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Short Film', 'Sport',
    'Superhero', 'Thriller', 'War', 'Western'
]


def add_genre(name):
    genre = Genre.objects.get_or_create(name=name)[0]
    genre.save()
    return genre


def add_movie(genre, imdb_id, name, description, pic_url, release_date, rating):
    movie = Movie.objects.get_or_create(imdb_id=imdb_id)
    movie.genre = genre
    movie.imdb_id = imdb_id
    movie.name = name
    movie.description = description
    movie.pic_url = pic_url
    movie.release_date = release_date
    movie.rating = rating

    movie.save()
    return movie


def add_review(movie, user, content, time, likes, rating):
    review = Review.objects.get_or_create(movie_id=movie.id)
    review.movie = movie
    review.user = user
    review.content = content
    review.time = time
    review.likes = likes
    review.rating = rating


if __name__ == '__main__':
    for genre in genres:
        add_genre(genre)
