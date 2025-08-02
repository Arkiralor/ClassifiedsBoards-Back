from django.db.models.signals import post_save, pre_save, pre_delete, post_delete

from classifieds_app.models import ClassifiedsAdvertisementComment, ClassifiedsAdvertisementImage, UserAdvertisementLike, UserSavedAdvertisement
from classifieds_app.constants import ClassifiedsConstants

from classifieds_app import logger


class ClassifiedsAdvertisementCommentSignals:
    MODEL = ClassifiedsAdvertisementComment

    @classmethod
    def created(cls, sender, instance: ClassifiedsAdvertisementComment, created, *args, **kwargs):
        if created:
            advertisement = instance.advertisement
            advertisement.score += ClassifiedsConstants.ONE_COMMENT_WEIGHT
            advertisement.save()
            logger.info(
                f"New comment for advertisement {advertisement.id} by {instance.user.email}.")

    @classmethod
    def updated(cls, sender, instance: ClassifiedsAdvertisementComment, created, *args, **kwargs):
        if not created:
            logger.info(
                f"Comment {instance.id} for advertisement {instance.advertisement.id} updated by {instance.user.email}.")

    @classmethod
    def deleted(cls, sender, instance: ClassifiedsAdvertisementComment, *args, **kwargs):
        advertisement = instance.advertisement
        advertisement.score -= ClassifiedsConstants.ONE_COMMENT_WEIGHT
        advertisement.save()


post_save.connect(receiver=ClassifiedsAdvertisementCommentSignals.created,
                  sender=ClassifiedsAdvertisementCommentSignals.MODEL)
post_save.connect(receiver=ClassifiedsAdvertisementCommentSignals.updated,
                  sender=ClassifiedsAdvertisementCommentSignals.MODEL)
post_delete.connect(receiver=ClassifiedsAdvertisementCommentSignals.deleted,
                    sender=ClassifiedsAdvertisementCommentSignals.MODEL)


class ClassifiedsAdvertisementImageSignals:
    MODEL = ClassifiedsAdvertisementImage

    @classmethod
    def deleted(cls, sender, instance: ClassifiedsAdvertisementImage, *args, **kwargs):
        instance.image.delete(save=False)
        logger.info(
            f"Image {instance.id} deleted from advertisement {instance.advertisement.id}.")


pre_delete.connect(receiver=ClassifiedsAdvertisementImageSignals.deleted,
                   sender=ClassifiedsAdvertisementImageSignals.MODEL)


class UserAdvertisementLikeSignals:
    MODEL = UserAdvertisementLike

    @classmethod
    def created(cls, sender, instance: UserAdvertisementLike, created, *args, **kwargs):
        if created:
            advertisement = instance.advertisement
            advertisement.score += ClassifiedsConstants.ONE_LIKE_WEIGHT
            advertisement.save()


post_save.connect(receiver=UserAdvertisementLikeSignals.created,
                  sender=UserAdvertisementLikeSignals.MODEL)


class UserSavedAdvertisementSignals:
    MODEL = UserSavedAdvertisement

    @classmethod
    def created(cls, sender, instance: UserSavedAdvertisement, created, *args, **kwargs):
        if created:
            logger.info(
                f"Advertisement {instance.advertisement.id} saved by user {instance.user.email}.")
            advertisement = instance.advertisement
            advertisement.score += ClassifiedsConstants.ONE_SAVE_WEIGHT
            advertisement.save()


post_save.connect(receiver=UserSavedAdvertisementSignals.created,
                  sender=UserSavedAdvertisementSignals.MODEL)
