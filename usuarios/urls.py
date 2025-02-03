from django.urls import path
from .views import login_view, dashboard_view

app_name = "usuarios"

urlpatterns = [
    path("login/", login_view, name="login"),
    
    path("dashboard/", dashboard_view, name="dashboard"),

]
