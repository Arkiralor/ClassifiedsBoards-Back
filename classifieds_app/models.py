from django.db import models

from core.boilerplate.model_template import TemplateModel
from user_app.models import User


class ClassifiedsCategory(TemplateModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            raise ValueError("Category name cannot be empty.")
        self.name = self.name.lstrip().rstrip().lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Classifieds Category"
        verbose_name_plural = "Classifieds Categories"
        ordering = ("name",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('name',)),
        )


class ClassifiedsAdvertisement(TemplateModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_advertisements')
    moderators = models.ManyToManyField(
        User, related_name='moderated_advertisements', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        ClassifiedsCategory, on_delete=models.CASCADE, related_name='advertisements')
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Classifieds Advertisement"
        verbose_name_plural = "Classifieds Advertisements"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('title',)),
            models.Index(fields=('category', 'creator',)),
        )


class ClassifiedsAdvertisementImage(TemplateModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    advertisement = models.ForeignKey(
        ClassifiedsAdvertisement, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/classifieds/')
    sequence_number = models.PositiveIntegerField(
        default=1, help_text="Order of the image in the advertisement")

    def __str__(self):
        return f"Image {self.title if self.title else 'No Title'} for {self.advertisement.title}"

    class Meta:
        verbose_name = "Classifieds Advertisement Image"
        verbose_name_plural = "Classifieds Advertisement Images"
        ordering = ("id", "sequence_number",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('advertisement',)),
        )


class ClassifiedsAdvertisementComment(TemplateModel):
    advertisement = models.ForeignKey(
        ClassifiedsAdvertisement, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.advertisement.title}"

    def save(self, *args, **kwargs):
        if not self.content:
            raise ValueError("Comment content cannot be empty.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Classifieds Advertisement Comment"
        verbose_name_plural = "Classifieds Advertisement Comments"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('advertisement', 'user')),
        )


class UserAdvertisementLike(TemplateModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liked_advertisements')
    advertisement = models.ForeignKey(
        ClassifiedsAdvertisement, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        verbose_name = "User Advertisement Like"
        verbose_name_plural = "User Advertisement Likes"
        unique_together = ('user', 'advertisement')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('advertisement',)),
        )


class UserSavedAdvertisement(TemplateModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='saved_advertisements')
    advertisement = models.ForeignKey(
        ClassifiedsAdvertisement, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        verbose_name = "User Saved Advertisement"
        verbose_name_plural = "User Saved Advertisements"
        unique_together = ('user', 'advertisement')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('advertisement',)),
        )
