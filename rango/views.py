import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page, Genre, Movie, Review

from datetime import datetime


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': category_list,
        'pages': page_list
    }

    visitor_cookie_handler(request)

    return render(request, 'rango/index.html', context=context_dict)


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
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', context={
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })


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


def get_movie_list_response(request, data_list, page, list_title, url_prefix=None):
    p = Paginator(data_list, 12)
    movie_page = p.page(page)

    if not url_prefix:
        url_prefix = re.findall('(.*/)\d+', request.path)
        url_prefix = url_prefix[0] if url_prefix else request.path

    if p.num_pages > 11:
        if page + 5 > p.num_pages:
            page_range = range(p.num_pages - 10, p.num_pages + 1)
        elif page - 5 < 1:
            page_range = range(1, 12)
        else:
            page_range = range(page - 5, page + 5 + 1)
    else:
        page_range = p.page_range

    return render(request, 'rango/movie.html', context={
        'list_title': list_title,
        'movie_page': movie_page,
        'page_range': page_range,
        'current_page': page,
        'url_prefix': url_prefix
    })


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
