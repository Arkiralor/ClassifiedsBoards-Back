from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from classifieds_app.helpers import ClassifiedsCategoryHelper, ClassifiedsAdvertisementHelper, ClassifiedsAdvertisementImageHelper


class ClassifiedsCategorySearchAPIView(APIView):
    permission_classes = (IsAuthenticated | IsAdminUser | AllowAny,)

    def get(self, request: Request) -> Response:
        query = request.query_params.get('query', None)
        page_no = int(request.query_params.get('page_no', 1))

        resp = ClassifiedsCategoryHelper.search(
            query=query, return_obj=False, page_no=page_no)

        return resp.to_response()

    def post(self, request: Request) -> Response:
        page_no = int(request.data.get('page_no', 1))
        resp = ClassifiedsCategoryHelper.list(page_no=page_no)

        return resp.to_response()


class ClassifiedsCategoryAPIView(APIView):
    permission_classes = (IsAuthenticated | IsAdminUser,)

    def get(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        name = request.query_params.get('name', None)

        resp = ClassifiedsCategoryHelper.get(
            pk=pk, name=name, return_obj=False)
        return resp.to_response()

    def post(self, request: Request) -> Response:
        data = request.data
        resp = ClassifiedsCategoryHelper.create(data=data, return_obj=False)
        return resp.to_response()

    def patch(self, request: Request) -> Response:
        data = request.data
        user = request.user
        pk = request.query_params.get('pk', None)
        resp = ClassifiedsCategoryHelper.update(
            data=data, user=user, category_id=pk, return_obj=False)
        return resp.to_response()

    def delete(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        resp = ClassifiedsCategoryHelper.delete(
            user=request.user, category_id=pk, return_obj=False)
        return resp.to_response()


class ClassifiedsAdvertisementSearchAPIView(APIView):
    permission_classes = (IsAuthenticated | IsAdminUser | AllowAny,)

    def get(self, request: Request) -> Response:
        query = request.query_params.get('query', None)
        page_no = int(request.query_params.get('page_no', 1))

        resp = ClassifiedsAdvertisementHelper.search(
            query=query, return_obj=False, page_no=page_no)

        return resp.to_response()

    def post(self, request: Request) -> Response:
        page_no = int(request.data.get('page_no', 1))
        resp = ClassifiedsAdvertisementHelper.list(page_no=page_no)

        return resp.to_response()


class ClassifiedsAdvertisementAPIView(APIView):
    permission_classes = (IsAuthenticated | IsAdminUser | AllowAny,)

    def get(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        title = request.query_params.get('title', None)

        resp = ClassifiedsAdvertisementHelper.get_one(
            pk=pk, title=title, return_obj=False)
        return resp.to_response()

    def post(self, request: Request) -> Response:
        data = request.data
        resp = ClassifiedsAdvertisementHelper.create(
            data=data, return_obj=False)
        return resp.to_response()

    def put(self, request: Request) -> Response:
        data = request.data
        user = request.user
        pk = request.query_params.get('pk', None)

        resp = ClassifiedsAdvertisementHelper.update(
            data=data, user=user, pk=pk, return_obj=False)
        return resp.to_response()

    def delete(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        resp = ClassifiedsAdvertisementHelper.delete(
            user=request.user, pk=pk)
        return resp.to_response()


class ClassifiedsAdvertisementImageAPIView(APIView):
    permission_classes = (IsAuthenticated | IsAdminUser,)

    def get(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        resp = ClassifiedsAdvertisementImageHelper.get_for_advertisement(
            pk=pk, return_obj=False)
        return resp.to_response()

    def post(self, request: Request) -> Response:
        data = request.data
        resp = ClassifiedsAdvertisementImageHelper.create(
            user=request.user, data=data, return_obj=False)
        return resp.to_response()

    def put(self, request: Request) -> Response:
        data = request.data
        user = request.user
        pk = request.query_params.get('pk', None)

        resp = ClassifiedsAdvertisementImageHelper.update(
            data=data, user=user, pk=pk, return_obj=False)
        return resp.to_response()

    def delete(self, request: Request) -> Response:
        pk = request.query_params.get('pk', None)
        resp = ClassifiedsAdvertisementImageHelper.delete(
            user=request.user, pk=pk)
        return resp.to_response()
