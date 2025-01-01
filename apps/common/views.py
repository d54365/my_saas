from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .pagination import PageNumberPagination


class BaseReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    service = None
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    serializer_action_classes = {}

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, self.serializer_class)

    def get_object_or_404(self, pk):
        instance = self.service.get_by_id(pk)
        if not instance:
            raise NotFound(detail="The requested resource was not found.")
        return instance


class BaseModelViewSet(
    BaseReadOnlyModelViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    def validate_and_perform_action(
        self, serializer_class, instance=None, service_method=None
    ):
        serializer = serializer_class(
            instance, data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        if instance and service_method:
            return service_method(
                instance, serializer.validated_data, self.request.user
            )

        if service_method:
            return service_method(serializer.validated_data, self.request.user)

        return serializer.validated_data

    def create(self, request, *args, **kwargs):
        obj = self.validate_and_perform_action(
            serializer_class=self.get_serializer_class(),
            service_method=self.service.create,
        )
        return Response(
            self.serializer_class(instance=obj).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object_or_404(kwargs[self.lookup_field])
        updated_instance = self.validate_and_perform_action(
            serializer_class=self.get_serializer_class(),
            instance=instance,
            service_method=self.service.update,
        )
        return Response(self.serializer_class(instance=updated_instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object_or_404(kwargs[self.lookup_field])
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        self.service.soft_delete(instance, self.request.user)
