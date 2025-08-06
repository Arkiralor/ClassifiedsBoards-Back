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
from database.custom_orm_functions.weighted_trigram_similarity import WeightedTrigramSimilarity
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

        query = query.lstrip().rstrip().lower()
        objs = objs.filter(
            Q(name__trigram_similar=query)
            | Q(description__trigram_similar=query)
        ).distinct().annotate(
            similarity=WeightedTrigramSimilarity(
                'name', query, 1.0) + WeightedTrigramSimilarity('description', query, 1.0)
        ).order_by('-similarity')

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
            if not obj.exists():
                resp.error = f"INVALID CATEGORY ID"
                resp.message = f"Category with ID {category_id} does not exist."
                resp.status_code = status.HTTP_404_NOT_FOUND

                logger.warning(resp.to_text())
                return resp
        elif name and not category_id and not name == StringConstants.BLANK:
            obj = ClassifiedsCategory.objects.filter(name__iexact=name).first()
            if not obj.exists():
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

        obj = cls.get(category_id=category_id, return_obj=True)
        if obj.error:
            return obj

        deserialized = ClassifiedsCategoryIOSerializer(
            instance=obj.data, data=data, partial=True)
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

        obj = cls.get(category_id=category_id, return_obj=True)
        if obj.error:
            return obj

        obj.data.delete()
        resp.message = f"Category '{category_id}' deleted successfully."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp


class ClassifiedsAdvertisementHelper:

    EDITABLE_FIELDS = (
        'title',
        'description',
        'price',
        'category',
    )

    @classmethod
    def get_one(cls, user: User = None, pk: str = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()
        obj: ClassifiedsAdvertisement = None

        if not pk or not isinstance(pk, str) or pk == StringConstants.BLANK:
            resp.error = f"INVALID INPUT"
            resp.message = f"Advertisement ID must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        obj = ClassifiedsAdvertisement.objects.filter(pk=pk).first()
        if (not obj.creator == user) and (not user in obj.moderators.all()) and (not user.is_superuser) and (not obj.is_active):
            obj = None

        if not obj:
            resp.error = f"NOT FOUND"
            resp.message = f"Advertisement with ID {pk} does not exist or is inactive"
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        resp.message = f"Advertisement '{obj.title}' found successfully."
        resp.data = obj if return_obj else ClassifiedsAdvertisementDisplaySerializer(
            obj).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def list(cls, return_obj: bool = False, page_no: int = 1, *args, **kwargs) -> Resp:
        resp = Resp()
        objs: QuerySet[ClassifiedsAdvertisement] = ClassifiedsAdvertisement.objects.filter(
            is_active=True).order_by('-created')

        if not objs:
            resp.error = f"NO ADVERTISEMENTS FOUND"
            resp.message = f"No advertisements available."
            resp.status_code = status.HTTP_404_NOT_FOUND

            logger.warning(resp.to_text())
            return resp

        paginator = Paginator(objs, django_settings.MAX_ITEMS_PER_PAGE)
        page = paginator.get_page(page_no)

        resp.message = f"Advertisements found successfully."
        resp.data = page if return_obj else ClassifiedsAdvertisementDisplaySerializer(
            page, many=True).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def search(cls, query: str = None, return_obj: bool = False, page_no: int = 1, *args, **kwargs) -> Resp:
        resp = Resp()

        if not isinstance(query, str):
            resp.error = f"INVALID INPUT"
            resp.message = f"Search query must be a string."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        query = query.lstrip().rstrip().lower() if query else None
        if not query or query == StringConstants.BLANK:
            resp.message = f"No search query provided. Returning all advertisements."
            objs = ClassifiedsAdvertisement.objects.filter(
                is_active=True).order_by('-created')
            resp.data = objs if return_obj else ClassifiedsAdvertisementOutputSerializer(
                objs, many=True).data
            resp.status_code = status.HTTP_200_OK

            logger.info(resp.to_text())
            return resp

        objs = ClassifiedsAdvertisement.objects.filter(
            Q(is_active=True)
            & Q(
                Q(title__trigram_similar=query)
                | Q(description__trigram_similar=query)
                | Q(category__name__trigram_similar=query)
            )
        ).distinct().annotate(
            similarity=WeightedTrigramSimilarity('title', query, 1.5)
            + WeightedTrigramSimilarity('description', query, 1.2)
            + WeightedTrigramSimilarity('category__name', query, 1.0)
        ).order_by('-similarity')

        paginated = Paginator(objs, django_settings.MAX_ITEMS_PER_PAGE)
        page = paginated.get_page(page_no)

        resp.message = f"Advertisements found successfully matching the query '{query}'."
        resp.data = page if return_obj else ClassifiedsAdvertisementDisplaySerializer(
            page, many=True).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def create(cls, user: User = None, data: dict = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user or not isinstance(user, User):
            resp.error = f"INVALID INPUT"
            resp.message = f"User must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        if not data or not isinstance(data, dict):
            resp.error = f"INVALID INPUT"
            resp.message = f"Data must be a dictionary."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        category = data.get('category')
        if isinstance(category, dict):
            create_category = ClassifiedsCategoryHelper.create(
                data=category, return_obj=True)
            if create_category.error:
                return create_category
            data['category'] = create_category.data.id

        data['creator'] = user.id
        # Default to inactive until approved by SITE moderators
        data['is_active'] = False
        deserialized = ClassifiedsAdvertisementInputSerializer(data=data)
        if not deserialized.is_valid():
            resp.error = f"INVALID DATA"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        deserialized.save()
        resp.message = f"Advertisement '{deserialized.data.get('title')}' created successfully."
        resp.data = deserialized.instance if return_obj else ClassifiedsAdvertisementDisplaySerializer(
            deserialized.instance).data
        resp.status_code = status.HTTP_201_CREATED

        logger.warning(resp.to_text())
        return resp

    def update(cls, user: User = None, pk: str = None, data: dict = None, return_obj: bool = False, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user or not isinstance(user, User):
            resp.error = f"INVALID INPUT"
            resp.message = f"User must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        if not pk or not isinstance(pk, str) or pk == StringConstants.BLANK:
            resp.error = f"INVALID INPUT"
            resp.message = f"Advertisement ID must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        if not data or not isinstance(data, dict):
            resp.error = f"INVALID INPUT"
            resp.message = f"Data must be a dictionary."
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

        obj = cls.get_one(user=user, pk=pk, return_obj=True)
        if obj.error:
            return obj

        if not obj.data.creator == user and not user in obj.data.moderators.all() and not user.is_superuser:
            resp.error = f"UNAUTHORIZED"
            resp.message = f"User is not authorized to update this advertisement."
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warning(resp.to_text())
            return resp

        deserialized = ClassifiedsAdvertisementInputSerializer(
            instance=obj.data, data=data, partial=True)
        if not deserialized.is_valid():
            resp.error = f"INVALID DATA"
            resp.message = f"{deserialized.errors}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        deserialized.save()
        resp.message = f"Advertisement '{deserialized.instance.title}' updated successfully."
        resp.data = deserialized.instance if return_obj else ClassifiedsAdvertisementDisplaySerializer(
            deserialized.instance).data
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp

    @classmethod
    def delete(cls, user: User = None, pk: str = None, *args, **kwargs) -> Resp:
        resp = Resp()

        if not user or not isinstance(user, User):
            resp.error = f"INVALID INPUT"
            resp.message = f"User must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        if not pk or not isinstance(pk, str) or pk == StringConstants.BLANK:
            resp.error = f"INVALID INPUT"
            resp.message = f"Advertisement ID must be provided."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warning(resp.to_text())
            return resp

        obj = cls.get_one(user=user, pk=pk, return_obj=True)
        if obj.error:
            return obj

        if not obj.data.creator == user and not user in obj.data.moderators.all() and not user.is_superuser:
            resp.error = f"UNAUTHORIZED"
            resp.message = f"User is not authorized to delete this advertisement."
            resp.status_code = status.HTTP_403_FORBIDDEN

            logger.warning(resp.to_text())
            return resp

        obj.data.delete()
        resp.message = f"Advertisement '{pk}' deleted successfully."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.to_text())
        return resp
