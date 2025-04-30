from django.urls import path
from . import views 
from chatdoctor.views import RegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.index, name='index'),
    path('process_symptom/', views.process_symptom, name='process_symptom'),
    path('get_additional_symptoms/', views.get_additional_symptoms, name='get_additional_symptoms'),
    path('process_diagnosis/', views.process_diagnosis, name='process_diagnosis'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]