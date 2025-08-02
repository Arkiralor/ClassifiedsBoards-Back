from django.contrib import admin

from classifieds_app.models import ClassifiedsCategory, ClassifiedsAdvertisement, ClassifiedsAdvertisementImage, ClassifiedsAdvertisementComment, \
    UserAdvertisementLike, UserSavedAdvertisement

@admin.register(ClassifiedsCategory)
class ClassifiedsCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-created',)
    list_filter = ('created', 'updated')

@admin.register(ClassifiedsAdvertisement)
class ClassifiedsAdvertisementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'creator', 'created')
    search_fields = ('title', 'description', 'creator__username', 'creator__email', 'category__name')
    ordering = ('-created',)
    raw_id_fields = ('category',)
    list_filter = ('category', 'created')
