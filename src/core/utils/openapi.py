from drf_yasg.inspectors import SwaggerAutoSchema


class CustomAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys
        tags = self.overrides.get('tags', getattr(self.view, 'tags', []))

        if not tags:
            tags = [operation_keys[0]]

        return tags
