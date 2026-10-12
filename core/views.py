from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView
from django.db.models import Q

from .forms import PostForm
from .models import Post


def searched_posts(query="", excluded_labels=None):
	posts = Post.objects.filter(is_hidden=False).order_by("-created_at")
	if query:
		posts = posts.filter(
			Q(title__icontains=query)
			| Q(content__icontains=query)
			| Q(author__username__icontains=query)
		)
	label_fields = {
		"profanity": "has_explicit_langauge",
		"external-links": "has_external_links",
		"long": "is_long_read",
	}
	for label in excluded_labels or []:
		if label in label_fields:
			posts = posts.filter(**{label_fields[label]: False})
	return posts


class HomeView(TemplateView):
	template_name = "core/home.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		query = self.request.GET.get("q", "").strip()
		excluded_labels = self.request.GET.getlist("exclude")
		posts = searched_posts(query, excluded_labels)
		context["posts"] = posts.filter(section=Post.Section.FOLLOWING)[:6]
		context["trending_posts"] = posts.filter(section=Post.Section.TRENDING)[:2]
		context["newbie_posts"] = posts.filter(section=Post.Section.NEWBIES)[:2]
		context["search_query"] = query
		context["excluded_labels"] = excluded_labels
		return context


class PostListView(ListView):
	model = Post
	template_name = "core/post_list.html"
	context_object_name = "posts"

	def get_queryset(self):
		self.search_query = self.request.GET.get("q", "").strip()
		self.excluded_labels = self.request.GET.getlist("exclude")
		return searched_posts(self.search_query, self.excluded_labels)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.search_query
		context["excluded_labels"] = self.excluded_labels
		return context


class PostDetailView(DetailView):
	model = Post
	template_name = "core/post_detail.html"
	context_object_name = "post"
	slug_field = "slug"
	slug_url_kwarg = "slug"


def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect("core:home")
	else:
		form = UserCreationForm()
	return render(request, "registration/register.html", {"form": form})


@login_required
def create_post(request):
	if request.method == "POST":
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.save()
			return redirect("core:home")
	else:
		form = PostForm()
	return render(request, "core/create_post.html", {"form": form})