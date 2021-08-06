import os
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class SmokeTestCase(TestCase):
    def test_smoke(self):
        self.assertEqual(1+1,2)

# Test: user creation
def create_user():
    user = User.objects.get_or_create(username='testuser')[0]
    user.set_password('000000')
    user.save()
    return user


# Test: url redirects
class PagesResponseTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code, 200)

    def test_about(self):
        response = self.client.get('/about/')
        self.assertTrue(response.status_code, 200)

    def test_category(self):
        response = self.client.get('/add_category/')
        self.assertTrue(response.status_code, 200)

    def test_register(self):
        response = self.client.get('/register/')
        self.assertTrue(response.status_code, 200)

    def test_login(self):
        response = self.client.get('/login/')
        self.assertTrue(response.status_code, 200)

    def test_restricted(self):
        response = self.client.get('/restricted/')
        self.assertTrue(response.status_code, 200)

    def test_logout(self):
        response = self.client.get('/logout/')
        self.assertTrue(response.status_code, 200)

    def test_movies(self):
        response = self.client.get('/movies/')
        self.assertTrue(response.status_code, 200)

    def test_movies_top(self):
        response = self.client.get('/movies/top/')
        self.assertTrue(response.status_code, 200)

    def test_movies_latest(self):
        response = self.client.get('/movies/latest/')
        self.assertTrue(response.status_code, 200)

    def test_movies_search(self):
        response = self.client.get('/movies/search/')
        self.assertTrue(response.status_code, 200)

    def test_genres(self):
        response = self.client.get('/genres/')
        self.assertTrue(response.status_code, 200)

    def test_reviews(self):
        response = self.client.get('/reviews/')
        self.assertTrue(response.status_code, 200)

    def test_reviews_popular(self):
        response = self.client.get('/reviews/popular/')
        self.assertTrue(response.status_code, 200)

    def test_reviews_like(self):
        response = self.client.get('/reviews/like/')
        self.assertTrue(response.status_code, 200)


# Test:  html files
class TemplatesTest(TestCase):

    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.templates_dir = os.path.join(self.project_base_dir, 'templates')
        self.app_templates_dir = os.path.join(self.templates_dir, 'rango')

    def test_templates_exist(self):
        about_path = os.path.join(self.app_templates_dir, 'about.html')
        add_category_path = os.path.join(self.app_templates_dir, 'add_category.html')
        add_page_path = os.path.join(self.app_templates_dir, 'add_page.html')
        base_path = os.path.join(self.app_templates_dir, 'base.html')
        category_path = os.path.join(self.app_templates_dir, 'category.html')
        genres_path = os.path.join(self.app_templates_dir, 'genres.html')
        index_path = os.path.join(self.app_templates_dir, 'index.html')
        login_path = os.path.join(self.app_templates_dir, 'login.html')
        movie_path = os.path.join(self.app_templates_dir, 'movie.html')
        movie_detail_path = os.path.join(self.app_templates_dir, 'movie_detail.html')
        register_path = os.path.join(self.app_templates_dir, 'base.html')
        restricted_path = os.path.join(self.app_templates_dir, 'restricted.html')
        reviews_path = os.path.join(self.app_templates_dir, 'reviews.html')
        self.assertTrue(os.path.isfile(about_path), f"Your about.html template does not exist")
        self.assertTrue(os.path.isfile(add_category_path), f"Your add_category.html template does not exist")
        self.assertTrue(os.path.isfile(add_page_path), f"Your add_page.html template does not exist")
        self.assertTrue(os.path.isfile(base_path), f"Your base.html template does not exist")
        self.assertTrue(os.path.isfile(category_path), f"Your category.html template does not exist")
        self.assertTrue(os.path.isfile(genres_path), f"Your genres.html template does not exist")
        self.assertTrue(os.path.isfile(index_path), f"Your index.html template does not exist")
        self.assertTrue(os.path.isfile(login_path), f"Your login.html template does not exist")
        self.assertTrue(os.path.isfile(movie_path), f"Your movie.html template does not exist")
        self.assertTrue(os.path.isfile(movie_detail_path), f"Your movie_detail.html template does not exist")
        self.assertTrue(os.path.isfile(register_path), f"Your register.html template does not exist")
        self.assertTrue(os.path.isfile(restricted_path), f"Your restricted.html template does not exist")
        self.assertTrue(os.path.isfile(reviews_path), f"Your reviews.html template does not exist")


# Test: basic authentication check
class AuthenticateTest(TestCase):

    def test_add_category(self):
        user = create_user()
        self.client.login(username=user.username, password=user.password)

        response = self.client.get(reverse('rango:add_category'))
        self.assertTrue(response.status_code, 200)

    def test_user_logout(self):
        user = create_user()
        self.client.login(username=user.username, password=user.password)

        response = self.client.get(reverse('rango:logout'))
        self.assertTrue(response.status_code, 200)
