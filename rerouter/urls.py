from django.urls import include, path

from . import views

app_name = 'rerouter'

urlpatterns = [
    path('webhook/<uuid:token>/<str:user>/', views.ingress, name="ingress"),
]
