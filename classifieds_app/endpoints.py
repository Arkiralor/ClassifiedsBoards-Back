from django.urls import path

from classifieds_app.apis import ClassifiedsCategoryAPIView, ClassifiedsCategorySearchAPIView, ClassifiedsAdvertisementSearchAPIView, ClassifiedsAdvertisementAPIView, \
    ClassifiedsAdvertisementImageAPIView

PREFIX = "api/classifieds/"

urlpatterns = [
    path('category/search/', ClassifiedsCategorySearchAPIView.as_view(), name='classifieds-category-search'),
    path('category/manage/', ClassifiedsCategoryAPIView.as_view(), name='classifieds-category-detail'),
    path('advertisement/search/', ClassifiedsAdvertisementSearchAPIView.as_view(), name='classifieds-advertisement-search'),
    path('advertisement/manage/', ClassifiedsAdvertisementAPIView.as_view(), name='classifieds-advertisement-detail'),
    path('image/manage/', ClassifiedsAdvertisementImageAPIView.as_view(), name='classifieds-advertisement-image-detail'),
]