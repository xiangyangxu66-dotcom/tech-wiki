from rest_framework import serializers
from .models import Category, Note, AuditLog, SystemConfig


class RecursiveCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    note_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 'note_count']

    def get_children(self, obj):
        children = obj.get_children()
        if children.exists():
            return RecursiveCategorySerializer(children, many=True).data
        return []

    def get_note_count(self, obj):
        return obj.notes.count()


class CategoryFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class NoteListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True, default=None)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    _snippet = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug',
            'category', 'category_name', 'category_slug',
            'note_tags', 'has_mermaid', 'bookmark', 'status', 'status_label',
            'created_at', 'updated_at',
            '_snippet',
        ]

    def get__snippet(self, obj):
        return self.context.get('_snippets', {}).get(obj.id)


class NoteDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True, default=None)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'content',
            'category', 'category_name', 'category_slug',
            'note_tags', 'has_mermaid',
            'bookmark', 'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'note_tags']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'model_name', 'object_id',
                  'summary', 'created_at']


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'description', 'updated_at']
        read_only_fields = ['key']
