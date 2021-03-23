from django.urls import path
from .views import homePageView
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
urlpatterns = [
    path('', homePageView, name='home'),
   path('openapi/', get_schema_view(
        title="Moco Documentation",
        description="API Description"
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='documenation.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]