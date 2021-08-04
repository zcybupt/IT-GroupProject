import os
import django
import json
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

django.setup()

from django.contrib.auth.models import User
from rango.models import Genre, Movie, Review, UserProfile

genres = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
    'Film Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Short Film', 'Sport',
    'Superhero', 'Thriller', 'War', 'Western'
]


def add_genre(name):
    genre = Genre.objects.get_or_create(name=name)[0]
    genre.save()
    return genre


def add_movie(genres, imdb_id, name, description, pic_url, release_year, rating):
    movie = Movie.objects.get_or_create(imdb_id=imdb_id)[0]
    movie.genres = ''.join(genres)
    movie.imdb_id = imdb_id
    movie.name = name
    movie.description = description
    movie.pic_url = pic_url
    movie.release_year = release_year
    movie.rating = rating

    movie.save()
    return movie


def add_user(username):
    user = User.objects.get_or_create(username=username)[0]
    user.set_password('000000')
    user.save()

    user_profile = UserProfile.objects.get_or_create(user_id=user.id)[0]
    user_profile.save()

    return user


def add_review(movie, user, title, content, time, likes, rating):
    review = Review.objects.create(movie=movie, user=user)
    review.title = title
    review.content = content
    review.time = time
    review.likes = likes
    review.rating = rating

    review.save()


def populate_data():
    # populate genres
    for genre in genres:
        add_genre(genre)

    # populate users, movies, reviews
    with open('imdb_top250.json', 'r') as f:
        for line in f:
            jo = json.loads(line)
            print('adding: %s' % jo.get('name'))
            movie = add_movie(
                genres=','.join(jo.get('genres')),
                imdb_id=jo.get('imdb_id'),
                name=jo.get('name'),
                description=jo.get('description'),
                pic_url=jo.get('pic_url'),
                release_year=jo.get('release_year'),
                rating=jo.get('rating')
            )

            for review in jo.get('reviews'):
                user = add_user(username=review.get('user'))
                content = review.get('content')
                add_review(
                    movie=movie,
                    user=user,
                    title=review.get('title'),
                    content=content[0] if len(content) == 1 else content,
                    time=datetime.strptime(review['time'], '%d %B %Y').replace(tzinfo=timezone.utc),
                    likes=review['likes'],
                    rating=review['rating']
                )


if __name__ == '__main__':
    populate_data()
