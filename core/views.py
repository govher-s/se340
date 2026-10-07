from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from .forms import PostForm
from .models import Post

# Create your views here.
def home(request):
    posts = Post.objects.all()

    hide_explicit = request.GET.get("hide_explicit")
    hide_long_reads = request.GET.get("hide_long_reads")
    hide_external_links = request.GET.get("hide_external_links")

    if hide_explicit:
        posts = posts.filter(has_explicit_language=False)

    if hide_long_reads:
        posts = posts.filter(is_long_read=False)

    if hide_external_links:
        posts = posts.filter(has_external_links=False)

    posts = posts.order_by("-created_at")

    return render(
        request,
        "core/home.html",
        {
            "posts": posts,
            "hide_explicit": hide_explicit,
            "hide_long_reads": hide_long_reads,
            "hide_external_links": hide_external_links,
        }
    )

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form}
    )

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect("home")

    else:
        form = PostForm()

    return render(
        request,
        "core/create_post.html",
        {"form": form}
    )