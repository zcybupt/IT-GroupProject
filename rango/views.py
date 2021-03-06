import json
import re
from datetime import datetime, timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rango.forms import CategoryForm, PageForm
from rango.models import Category, Page, Genre, Movie, Review, UserProfile


def index(request):
    carousel_movies = Movie.objects.all().order_by('-rating')[:5]

    editor_picks = Movie.objects.all().order_by('-release_year')[:6]

    return render(request, 'rango/index.html', context={
        'carousel_movies': carousel_movies,
        'editor_picks': editor_picks
    })


def about(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    return render(request, 'rango/about.html', context={
        'visits': visits
    })


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)

        context_dict['category'] = category
        context_dict['pages'] = Page.objects.filter(category=category)
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None

    if not category: return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        profile = UserProfile.objects.create(user=user)
        profile.save()

        return redirect(reverse('rango:login'))
    else:
        return render(request, 'rango/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val: val = default_val

    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def get_paginator(data_list, page):
    p = Paginator(data_list, 12)
    paginator = p.page(page)

    if p.num_pages > 11:
        if page + 5 > p.num_pages:
            page_range = range(p.num_pages - 10, p.num_pages + 1)
        elif page - 5 < 1:
            page_range = range(1, 12)
        else:
            page_range = range(page - 5, page + 5 + 1)
    else:
        page_range = p.page_range

    return page_range, paginator


def get_movie_list_response(request, data_list, page, list_title, url_prefix=None):
    page_range, paginator = get_paginator(data_list, page)

    if not url_prefix:
        url_prefix = re.findall('(.*/)\d+', request.path)
        url_prefix = url_prefix[0] if url_prefix else request.path

    return render(request, 'rango/movie.html', context={
        'list_title': list_title,
        'movie_page': paginator,
        'page_range': page_range,
        'current_page': page,
        'url_prefix': url_prefix
    })


def get_movie(request, movie_id, page=1):
    movie = Movie.objects.get(id=movie_id)
    reviews = Review.objects.filter(movie=movie).order_by('-likes')

    genres = movie.genres.split(',')
    countries = movie.countries.replace(',', '/')
    directors = movie.directors.replace(',', '/')
    actors = movie.actors.replace(',', '/')

    page_range, paginator = get_paginator(reviews, page)

    res = re.findall('\d+', request.path)
    url_prefix = '/rango/movies/%s/' % res[0]

    print(request.user.username)

    return render(request, 'rango/movie_detail.html', context={
        'movie': movie,
        'genres': genres,
        'countries': countries,
        'directors': directors,
        'actors': actors,
        'review_page': paginator,
        'page_range': page_range,
        'current_page': page,
        'url_prefix': url_prefix,
        'is_logged_in': request.user.username != ''
    })


def add_movie_review(request, movie_id):
    if not request.user.username:
        return HttpResponse(
            json.dumps({
                'success': False,
                'msg': 'login required'
            }),
            content_type='application/json'
        )

    if request.method == 'POST' and request.body:
        data = json.loads(request.body)
        movie = Movie.objects.get(id=movie_id)

        title = data.get('title')
        content = data.get('content')
        rating = data.get('rating')
        review_time = datetime.now(tz=timezone.utc)

        rating = 2 * int(re.findall('\d', rating)[0])

        review = Review.objects.create(
            movie=movie,
            user=request.user,
            title=title,
            content=content,
            time=review_time,
            likes=0,
            rating=rating
        )

        review.save()

        return HttpResponse(
            json.dumps({
                'success': True,
                'review_id': review.id,
                'rating': rating,
                'username': request.user.username
            }),
            content_type='application/json'
        )
    else:
        return HttpResponse(
            json.dumps({'success': False}),
            content_type='application/json'
        )


def get_top_movies(request, page=1):
    all_movies = Movie.objects.filter().order_by('-rating')
    return get_movie_list_response(request, all_movies, page, 'TOP 250 MOVIES')


def get_latest_movies(request, page=1):
    all_movies = Movie.objects.filter().order_by('-release_year')
    return get_movie_list_response(request, all_movies, page, 'LATEST MOVIES')


def search_movies(request):
    keyword = request.GET.get('keyword')

    results = Movie.objects.filter(name__icontains=keyword).order_by('-rating')

    return get_movie_list_response(request, results, 1, 'RELATED MOVIES', request.path + keyword + '/')


def search_more_movies(request, keyword, page=1):
    results = Movie.objects.filter(name__icontains=keyword).order_by('-rating')

    return get_movie_list_response(request, results, page, 'RELATED MOVIES')


def get_movies_by_genre(request, genre=None, page=1):
    if not genre:
        genres = Genre.objects.all()

        return render(request, 'rango/genres.html', context={'genres': genres})

    movie_list = Movie.objects.filter(genres__contains=genre).order_by('-rating')

    return get_movie_list_response(request, movie_list, page, genre.upper() + ' MOVIES')


def get_review_list_response(request, data_list, page, list_title, url_prefix=None, user=None,):
    page_range, paginator = get_paginator(data_list, page)

    if not url_prefix:
        url_prefix = re.findall('(.*/)\d+', request.path)
        url_prefix = url_prefix[0] if url_prefix else request.path

    return render(request, 'rango/reviews.html', context={
        'review_page': paginator,
        'page_range': page_range,
        'current_page': page,
        'url_prefix': url_prefix,
        'user': user,
        'list_title': list_title
    })


def get_popular_reviews(request, page=1):
    all_reviews = Review.objects.filter().order_by('-likes').filter()
    return get_review_list_response(request, all_reviews, page, 'POPULAR REVIEWS')


def get_reviews_by_user(request, user_name, page=1):
    user = User.objects.filter(username=user_name).first()
    all_reviews = Review.objects.filter(user=user).order_by('-time')
    return get_review_list_response(request, all_reviews, page, user_name.upper() + '\'S REVIEWS', user)


def like_review(request):
    if not request.user.username:
        return HttpResponse(
            json.dumps({
                'success': False,
                'msg': 'login required'
            }),
            content_type='application/json'
        )

    if request.method == 'POST' and request.body:
        data = json.loads(request.body)
        review_id = data.get('review_id')

        review = Review.objects.get(id=review_id)
        review.likes = review.likes + 1
        review.save()

        return HttpResponse(
            json.dumps({
                'success': True,
                'likes': review.likes
            }),
            content_type='application/json'
        )
    else:
        return HttpResponse(
            json.dumps({'success': False}),
            content_type='application/json'
        )
