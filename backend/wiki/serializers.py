from rest_framework import serializers
from .models import Tag, Category, Note, AuditLog, SystemConfig


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']


class TagNameSerializer(serializers.ModelSerializer):
    """Note に埋め込む軽量タグ表現。"""
    class Meta:
        model = Tag
        fields = ['name', 'slug']


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Note
# ---------------------------------------------------------------------------
class NoteListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True, default=None)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    _snippet = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug',
            'category', 'category_name', 'category_slug',
            'tags', 'has_mermaid', 'bookmark', 'status', 'status_label',
            'created_at', 'updated_at',
            '_snippet',
        ]

    def get__snippet(self, obj):
        return self.context.get('_snippets', {}).get(obj.id)


class NoteDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    category_slug = serializers.CharField(source='category.slug', read_only=True, default=None)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    tags = TagNameSerializer(many=True, read_only=True)
    tag_slugs = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False,
        help_text='タグ slug の配列。書き込み時に content frontmatter と DB M2M を同期する'
    )

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'content',
            'category', 'category_name', 'category_slug',
            'tags', 'tag_slugs', 'has_mermaid',
            'bookmark', 'status', 'status_label',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug']

    def update(self, instance, validated_data):
        tag_slugs = validated_data.pop('tag_slugs', None)
        instance = super().update(instance, validated_data)
        if tag_slugs is not None:
            instance._set_tags_from_slugs(tag_slugs)
        return instance


# ---------------------------------------------------------------------------
# AuditLog / SystemConfig
# ---------------------------------------------------------------------------
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
