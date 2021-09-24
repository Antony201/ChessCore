from rest_framework import mixins


class DestroyModelMixin(mixins.DestroyModelMixin):
    ...


class HardDestroyModelMixin(mixins.DestroyModelMixin):
    def perform_destroy(self, instance):
        instance.delete(hard=True)
