import os
import django
import json
from datetime import datetime, timezone
from imdb_review_spider import download_covers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

django.setup()

from django.contrib.auth.models import User
from rango.models import Genre, Movie, Review, UserProfile

genres = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
    'Film Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport',
    'Superhero', 'Thriller', 'War', 'Western'
]


def add_genre(name):
    genre = Genre.objects.get_or_create(name=name)[0]
    genre.save()
    return genre


def add_movie(genres, imdb_id, name, runtime, countries, directors, actors,
              description, pic_url, release_year, rating):
    movie = Movie.objects.get_or_create(imdb_id=imdb_id)[0]
    movie.genres = ''.join(genres)
    movie.imdb_id = imdb_id
    movie.name = name
    movie.runtime = runtime
    movie.countries = ' / '.join(countries)
    movie.directors = ' / '.join(directors)
    movie.actors = ' / '.join(actors)
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


def populate_data(limit=None):
    # populate genres
    for genre in genres:
        add_genre(genre)

    # populate users, movies, reviews
    with open('imdb_top250.json', 'r') as f:
        for i, line in enumerate(f):
            if limit and i == limit:
                break
            jo = json.loads(line)
            print('adding: %s' % jo.get('name'))
            movie = add_movie(
                genres=','.join(jo.get('genres')),
                imdb_id=jo.get('imdb_id'),
                name=jo.get('name'),
                runtime=jo.get('runtime')[0],
                countries=jo.get('countries'),
                directors=jo.get('directors'),
                actors=jo.get('actors'),
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
    print('** It will take a very time to populate all the data. **')
    print('Do you want to fill in only 30 pieces of data instead?')
    print('y: 30 pieces\nn: all the data')
    res = input('Your choice: ')
    if res == 'y':
        populate_data(30)
        download_covers(30)
    elif res == 'n':
        populate_data()
        download_covers()
    else:
        print('Incorrect input.')
        exit(0)
