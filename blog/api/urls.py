from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('blog/',views.Blog.as_view()),
    path('get_all_blogs/',views.GetBlogs.as_view()),
    path('add_comment/',views.AddComment.as_view()),
    path('blog_reaction/',views.BlogReactions.as_view()),
    path('vote_reaction/',views.VoteReactions.as_view()),
    path('test/',views.test.as_view()),
    


]