from django.urls import path
from . import views
app_name = "core"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("posts/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]