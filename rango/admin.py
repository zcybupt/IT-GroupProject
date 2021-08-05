from django.contrib import admin
from rango.models import Category, Page, UserProfile, Movie, Review


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'genres', 'imdb_id' , 'release_year', 'rating')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class Reviewadmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'title', 'content', 'time', 'likes', 'rating')
admin.site.register(Movie, MovieAdmin)
#admin.site.register(Category, CategoryAdmin)
#admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
admin.site.register(Review, Reviewadmin)
