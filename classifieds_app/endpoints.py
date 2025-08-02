from django.urls import path

from classifieds_app.apis import ClassifiedsCategoryAPIView, ClassifiedsCategorySearchAPIView

PREFIX = "api/classifieds/"

urlpatterns = [
    path('search/', ClassifiedsCategorySearchAPIView.as_view(), name='classifieds-category-search'),
    path('manage/', ClassifiedsCategoryAPIView.as_view(), name='classifieds-category-detail'),
]