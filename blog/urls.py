from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='blog-main'),
    path('posts', views.all_posts, name='all-posts'),
    path('posts/create', views.create_post, name='create-post'),
    path('posts/search', views.search_posts, name='search-posts'),
    path('posts/<str:slug>', views.post_details, name='post-details'),
    path('posts/<str:slug>/edit', views.edit_post, name='edit-post'),
    path('posts/<str:slug>/rate', views.rate_post, name='rate-post'),
    path('posts/<str:slug>/delete', views.delete_post, name='delete-post'),
    path('posts/<str:slug>/comments', views.create_comment, name='create-comment'),
    path('posts/<str:slug>/comments/<int:comment_id>/edit', views.edit_comment, name='edit-comment'),
    path('tags/<str:tag>', views.posts_by_tag, name='posts-by-tag'),
    path('<str:username>/my-posts', views.posts_by_user, name='posts-by-user'),
    path('<str:username>/notifications', views.all_notifications, name='all-notifications'),
    path('notifications/<int:notification_id>/post/<slug:slug>', views.notification_view, name='notification')
]
