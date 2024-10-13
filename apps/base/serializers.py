from typing import Type

from rest_framework import serializers

from apps.base.models import BaseModel


class BaseModelSerializer(serializers.ModelSerializer):
    pass


class DynamicFilteringSerializer(serializers.Serializer):
    def __init__(self, model: Type[BaseModel], **kwargs):
        super().__init__(**kwargs)
        self._model = model

    filters = serializers.JSONField(required=False, default={})
    sort = serializers.JSONField(required=False, default={})

    def validate_filters(self, value):

        if value is None:
            return value

        if not isinstance(value, list):
            raise serializers.ValidationError("Filter must be a list.")

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Filter items must be dictionaries.")

            try:
                key = item['key']
                op = item['op']
                item_value = item['value']
            except KeyError:
                raise serializers.ValidationError("Filter items must have 'key', 'op', and 'value' keys.")

            if not hasattr(self._model, key):
                raise serializers.ValidationError(f"Invalid filter key: {key}")

            valid_ops = [
                'exact', 'iexact', 'contains', 'icontains', 'in', 'gt', 'gte', 'lt', 'lte',
                'startswith', 'endswith', 'istartswith', 'iendswith', 'regex', 'iregex'
            ]
            if op not in valid_ops:
                raise serializers.ValidationError(f"Invalid filter operation: {op}")

        return value

    def validate_sort(self, value):
        if value is None:
            return value

        if not isinstance(value, list):
            raise serializers.ValidationError("Sort must be a list.")

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Sort items must be dictionaries.")

            try:
                key = item['key']
                type = item['type']
            except KeyError:
                raise serializers.ValidationError("Sort items must have 'key' and 'type' keys.")

            valid_types = ['asc', 'desc']
            if type not in valid_types:
                raise serializers.ValidationError(f"Invalid sort type: {type}")

        return value


class BaseQuerySerializer(BaseModelSerializer):
    query = serializers.JSONField()
    page = serializers.IntegerField(required=False, default=1)
    limit = serializers.IntegerField(required=False, default=10)

    def validate_page(self, page):
        if page < 0:
            raise serializers.ValidationError("Invalid page number")
        else:
            return page

    def validate_limit(self, limit):
        if limit < 1 or limit > 100:
            raise serializers.ValidationError("Invalid limit")
        else:
            return limit
