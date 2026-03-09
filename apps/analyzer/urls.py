from django.urls import path
from apps.analyzer import views

app_name = 'analyzer'

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # Analyzer
    path('',                      views.homepage,       name='homepage'),
    path('analyze/',              views.analyze,        name='analyze'),
    path('dashboard/',            views.dashboard,      name='dashboard'),
    path('analysis/<int:pk>/',    views.analysis_detail, name='detail'),

    # Compare
    path('compare/',              views.compare_page,    name='compare'),
    path('compare/analyze/',      views.compare_analyze, name='compare_analyze'),
]