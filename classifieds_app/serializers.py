from rest_framework.serializers import ModelSerializer
from drf_base64.fields import Base64ImageField
from classifieds_app.models import ClassifiedsCategory, ClassifiedsAdvertisement, ClassifiedsAdvertisementImage, ClassifiedsAdvertisementComment, \
    UserAdvertisementLike, UserSavedAdvertisement
from user_app.serializers import ShowUserSerializer


class ClassifiedsCategoryIOSerializer(ModelSerializer):

    class Meta:
        model = ClassifiedsCategory
        fields = "__all__"


class ClassifiedsAdvertisementInputSerializer(ModelSerializer):

    class Meta:
        model = ClassifiedsAdvertisement
        fields = "__all__"


class ClassifiedsAdvertisementOutputSerializer(ModelSerializer):

    category = ClassifiedsCategoryIOSerializer(read_only=True)
    creator = ShowUserSerializer(read_only=True)
    moderators = ShowUserSerializer(many=True, read_only=True)

    class Meta:
        model = ClassifiedsAdvertisement
        fields = "__all__"


class ClassifiedsAdvertisementDisplaySerializer(ModelSerializer):

    category = ClassifiedsCategoryIOSerializer(read_only=True)
    creator = ShowUserSerializer(read_only=True)
    moderators = ShowUserSerializer(many=True, read_only=True)

    class Meta:
        model = ClassifiedsAdvertisement
        fields = (
            "id",
            "title",
            "description",
            "creator",
            "price",
            "category",
            "score",
            "is_active",
            "moderators"
        )


class ClassifiedsAdvertisementImageInputSerializer(ModelSerializer):

    class Meta:
        model = ClassifiedsAdvertisementImage
        fields = "__all__"


class ClassifiedsAdvertisementImageOutputSerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    advertisement = ClassifiedsAdvertisementOutputSerializer(read_only=True)

    class Meta:
        model = ClassifiedsAdvertisementImage
        fields = "__all__"


class ClassifiedsAdvertisementImageDisplaySerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    advertisement = ClassifiedsAdvertisementDisplaySerializer(read_only=True)

    class Meta:
        model = ClassifiedsAdvertisementImage
        fields = "__all__"


class ClassifiedsAdvertisementCommentInputSerializer(ModelSerializer):

    class Meta:
        model = ClassifiedsAdvertisementComment
        fields = "__all__"


class ClassifiedsAdvertisementCommentOutputSerializer(ModelSerializer):
    advertisement = ClassifiedsAdvertisementDisplaySerializer(read_only=True)
    user = ShowUserSerializer(read_only=True)

    class Meta:
        model = ClassifiedsAdvertisementComment
        fields = "__all__"


class UserAdvertisementLikeInputSerializer(ModelSerializer):

    class Meta:
        model = UserAdvertisementLike
        fields = "__all__"


class UserAdvertisementLikeOutputSerializer(ModelSerializer):
    advertisement = ClassifiedsAdvertisementDisplaySerializer(read_only=True)
    user = ShowUserSerializer(read_only=True)

    class Meta:
        model = UserAdvertisementLike
        fields = "__all__"


class UserSavedAdvertisementInputSerializer(ModelSerializer):

    class Meta:
        model = UserSavedAdvertisement
        fields = "__all__"


class UserSavedAdvertisementOutputSerializer(ModelSerializer):
    advertisement = ClassifiedsAdvertisementDisplaySerializer(read_only=True)
    user = ShowUserSerializer(read_only=True)

    class Meta:
        model = UserSavedAdvertisement
        fields = "__all__"
