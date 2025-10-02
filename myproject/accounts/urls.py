from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_video, name='upload_video'),
    path('notes/<int:note_id>/', views.view_notes, name='view_notes'),
    path('notes/pdf/<int:note_id>/', views.generate_pdf, name='generate_pdf'),
    path('upload-qna/', views.upload_qna, name='upload_qna'),
    path('view-qna/', views.view_qna, name='view_qna'),
]
