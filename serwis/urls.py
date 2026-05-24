from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls')),
    
    path('', views.home, name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('rowery/', views.rowery, name='rowery'),
    path('rowery/dodaj/', views.dodaj_rower, name='dodaj_rower'),

    path('zgloszenia/', views.zgloszenia, name='zgloszenia'),
    path('zgloszenia/dodaj/', views.dodaj_zgloszenie, name='dodaj_zgloszenie'),

    path('czesci/', views.czesci, name='czesci'),
]
