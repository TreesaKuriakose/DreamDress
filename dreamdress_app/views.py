from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Blog, Comment, UserProfile, Like
from django.contrib.auth.models import User
from .forms import UserProfileForm, CommentForm
from django.db.models import F
from django.http import JsonResponse

# Create your views here.

class BlogListView(ListView):
    model = Blog
    template_name = 'dreamdress_app/blog_list.html'
    context_object_name = 'blogs'
    ordering = ['-created_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get trending posts (top 8 by view count)
        context['trending_posts'] = Blog.objects.order_by('-view_count')[:8]
        # Get the maximum view count for percentage calculation
        max_views = Blog.objects.order_by('-view_count').first()
        context['max_views'] = max_views.view_count if max_views else 1
        return context

class BlogDetailView(DetailView):
    model = Blog
    template_name = 'dreamdress_app/blog_detail.html'
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['is_liked'] = self.object.is_liked_by(self.request.user)
        return context
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Increment the view count
        obj.view_count = F('view_count') + 1
        obj.save()
        # Refresh from db to get the actual incremented count
        obj.refresh_from_db()
        return obj

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'dreamdress_app/blog_form.html'
    fields = ['title', 'content', 'image']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = 'dreamdress_app/blog_form.html'
    fields = ['title', 'content', 'image']
    
    def test_func(self):
        blog = self.get_object()
        return self.request.user == blog.author

class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'dreamdress_app/blog_confirm_delete.html'
    success_url = reverse_lazy('blog-list')
    
    def test_func(self):
        blog = self.get_object()
        return self.request.user == blog.author

@login_required
def add_comment(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                blog=blog,
                author=request.user,
                content=content
            )
        return redirect('blog-detail', pk=pk)
    return redirect('blog-detail', pk=pk)

class UserProfileView(DetailView):
    model = UserProfile
    template_name = 'dreamdress_app/user_profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        return get_object_or_404(UserProfile, user__username=self.kwargs['username'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['user_blogs'] = Blog.objects.filter(author=user).order_by('-created_date')
        return context

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user-profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'dreamdress_app/edit_profile.html', {'form': form, 'profile': profile})

@login_required
def like_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        if blog.is_liked_by(request.user):
            blog.likes.remove(request.user)
            liked = False
        else:
            blog.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'like_count': blog.like_count
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)
