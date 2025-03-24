from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog-list'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('blog/new/', views.BlogCreateView.as_view(), name='blog-create'),
    path('blog/<int:pk>/update/', views.BlogUpdateView.as_view(), name='blog-update'),
    path('blog/<int:pk>/delete/', views.BlogDeleteView.as_view(), name='blog-delete'),
    path('blog/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('blog/<int:pk>/like/', views.like_blog, name='like-blog'),
] 