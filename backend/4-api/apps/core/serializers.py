from rest_framework import serializers


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()


class BulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class BulkResultSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    total = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.DictField())
