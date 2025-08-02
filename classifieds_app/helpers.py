from django.conf import settings as django_settings
from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import status

from core.boilerplate.response_template import Resp
from core.constants import StringConstants
from classifieds_app.models import ClassifiedsAdvertisement, ClassifiedsCategory, ClassifiedsAdvertisementImage, \
    ClassifiedsAdvertisementComment, UserAdvertisementLike, UserSavedAdvertisement
from classifieds_app.serializers import ClassifiedsAdvertisementCommentInputSerializer, ClassifiedsAdvertisementCommentOutputSerializer, \
    ClassifiedsAdvertisementInputSerializer, ClassifiedsAdvertisementOutputSerializer, ClassifiedsAdvertisementDisplaySerializer, \
    ClassifiedsAdvertisementImageDisplaySerializer, ClassifiedsAdvertisementImageInputSerializer, ClassifiedsAdvertisementImageOutputSerializer, \
    ClassifiedsCategoryIOSerializer, UserAdvertisementLikeInputSerializer, UserAdvertisementLikeOutputSerializer, UserSavedAdvertisementInputSerializer, \
    UserSavedAdvertisementOutputSerializer
from user_app.models import User

from classifieds_app import logger


class ClassifiedsCategoryHelper:

    EDITABLE_FIELDS = (
        'name',
        'description',
    )

    @classmethod
    def search(cls, query: str = None, return_obj: bool = False, page_no: int = 1, *args, **kwargs) -> Resp:
        resp = Resp()
        objs = ClassifiedsCategory.objects.all().order_by('name')

        if not query or query == StringConstants.BLANK:
            resp.message = f"No search query provided. Returning all categories."
            resp.data = objs if return_obj else ClassifiedsCategoryIOSerializer(
                objs, many=True).data
            resp.status_code = status.HTTP_200_OK

            logger.info(resp.to_text())
            return resp

        if not isinstance(query, str):
            resp.error = f"INVALID INPUT"
            resp.message = f"Search query must be a string."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        query = query.strip().lower()
        objs = objs.filter(
            Q(name__trigram_similar=query)
            | Q(description__trigram_similar=query)
        ).distinct().annotate(
            similarity=TrigramSimilarity(
                'name', query) + TrigramSimilarity('description', query)
        ).order_by('similarity')

        if not objs:
            resp.error = f"NO CATEGORIES FOUND"
            resp.message = f"No categories found matching the query '{query}'."
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        paginator = Paginator(objs, django_settings.MAX_ITEMS_PER_PAGE)
        page = paginator.get_page(page_no)

        resp.message = f"Categories found successfully matching the query '{query}'."
        resp.data = page if return_obj else ClassifiedsCategoryIOSerializer(
            page, many=True).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def get(cls, category_id: str = None, name: str = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()
        if not category_id and not name:
            resp.error = f"INVALID INPUT"
            resp.message = f"Either cCategory ID or NAME must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        if category_id and not name and not category_id == StringConstants.BLANK:
            obj = ClassifiedsCategory.objects.filter(pk=category_id).first()
            if not obj:
                resp.error = f"INVALID CATEGORY ID"
                resp.message = f"Category with ID {category_id} does not exist."
                resp.status_code = status.HTTP_404_NOT_FOUND

                logger.warning(resp.to_text())
                return resp
        elif name and not category_id and not name == StringConstants.BLANK:
            obj = ClassifiedsCategory.objects.filter(name__iexact=name).first()
            if not obj:
                resp.error = f"INVALID CATEGORY NAME"
                resp.message = f"Category with name {name} does not exist."
                resp.status_code = status.HTTP_404_NOT_FOUND

                logger.warning(resp.to_text())
                return resp
        else:
            resp.error = f"INVALID INPUT"
            resp.message = f"Either category ID or NAME must be provided, not both."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        resp.message = f"Category '{obj.name}' found successfully."
        resp.data = obj if return_obj else ClassifiedsCategoryIOSerializer(
            obj).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def list(cls, return_obj: bool = False, page_no: int = 1, *args, **kwargs) -> Resp:
        resp = Resp()

        categories = ClassifiedsCategory.objects.all().order_by('name')
        if not categories:
            resp.error = f"NO CATEGORIES FOUND"
            resp.message = f"No categories available."
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        paginator = Paginator(categories, django_settings.MAX_ITEMS_PER_PAGE)
        page = paginator.get_page(page_no)

        resp.message = f"Categories found successfully."
        resp.data = page if return_obj else ClassifiedsCategoryIOSerializer(
            page, many=True).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def create(cls, data: dict = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()

        if not data or not isinstance(data, dict):
            resp.error = f"INVALID INPUT"
            resp.message = f"Data must be a dictionary."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        deserialized = ClassifiedsCategoryIOSerializer(data=data)
        if not deserialized.is_valid():
            resp.error = f"INVALID DATA"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        deserialized.save()
        resp.message = f"Category '{deserialized.data.get('name')}' created successfully."
        resp.data = deserialized.data if return_obj else deserialized.instance
        resp.status_code = status.HTTP_201_CREATED

        logger.info(resp.to_text())
        return resp
    
    @classmethod
    def update(cls, user: User = None, category_id: str = None, data: dict = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user or not (user.is_superuser or not user.is_staff):
            resp.error = f"UNAUTHORIZED"
            resp.message = f"User is not authorized to update categories."
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warning(resp.to_text())
            return resp

        if not category_id or not data or not isinstance(data, dict):
            resp.error = f"INVALID INPUT"
            resp.message = f"Category ID and data must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        for key in data:
            if key not in cls.EDITABLE_FIELDS:
                resp.error = f"INVALID FIELD"
                resp.message = f"Field '{key}' is not editable."
                resp.status_code = status.HTTP_400_BAD_REQUEST

                logger.warning(resp.to_text())
                return resp

        obj = ClassifiedsCategory.objects.filter(pk=category_id).first()
        if not obj:
            resp.error = f"INVALID CATEGORY ID"
            resp.message = f"Category with ID {category_id} does not exist."
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        deserialized = ClassifiedsCategoryIOSerializer(
            instance=obj, data=data, partial=True)
        if not deserialized.is_valid():
            resp.error = f"INVALID DATA"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        deserialized.save()
        resp.message = f"Category '{deserialized.instance.name}' updated successfully."
        resp.data = deserialized.data if return_obj else deserialized.instance
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp
    
    @classmethod
    def delete(cls, user: User = None, category_id: str = None, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user or not (user.is_superuser or not user.is_staff):
            resp.error = f"UNAUTHORIZED"
            resp.message = f"User is not authorized to delete categories."
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warning(resp.to_text())
            return resp

        if not category_id:
            resp.error = f"INVALID INPUT"
            resp.message = f"Category ID must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        obj = ClassifiedsCategory.objects.filter(pk=category_id).first()
        if not obj:
            resp.error = f"INVALID CATEGORY ID"
            resp.message = f"Category with ID {category_id} does not exist."
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        obj.delete()
        resp.message = f"Category '{obj.name}' deleted successfully."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp
