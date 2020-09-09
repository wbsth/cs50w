from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.article, name="article"),
    path("search", views.search, name="search"),
    path("new", views.new_page, name="new_page"),
    path("random", views.random, name="random"),
    path("wiki/<str:name>/edit", views.edit, name="edit")
]
