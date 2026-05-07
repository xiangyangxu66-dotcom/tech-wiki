"""
Django Admin 設定。

- admin.site.disable_action('delete_selected') で誤操作防止（ソフトデリートなしのため）
- Mermaid 検出、タグ数、ブックマーク状態を list_display で確認可能
"""
from django.contrib import admin
from .models import Tag, Category, Note, AuditLog, SystemConfig

admin.site.disable_action('delete_selected')


# ============================================================
# Tag
# ============================================================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'note_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['slug', 'created_at']

    def get_queryset(self, request):
        from django.db.models import Count
        return super().get_queryset(request).annotate(_note_count=Count('notes'))

    @admin.display(description='ノート数', ordering='_note_count')
    def note_count(self, obj):
        return getattr(obj, '_note_count', 0)


# ============================================================
# Category
# ============================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    search_fields = ['name']
    readonly_fields = ['slug']


# ============================================================
# Note
# ============================================================
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'tag_display', 'bookmark', 'status', 'has_mermaid', 'updated_at']
    list_filter = ['status', 'bookmark', 'has_mermaid', 'category']
    search_fields = ['title', 'content']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    date_hierarchy = 'updated_at'

    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'slug', 'content')
        }),
        ('分類', {
            'fields': ('category', 'tags'),
        }),
        ('状態', {
            'fields': ('bookmark', 'status'),
        }),
        ('日時', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='タグ')
    def tag_display(self, obj):
        return ', '.join(t.name for t in obj.tags.all()) or '—'


# ============================================================
# AuditLog (ReadOnly)
# ============================================================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'model_name', 'object_id', 'username', 'created_at']
    list_filter = ['action', 'model_name']
    search_fields = ['username', 'summary']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# SystemConfig
# ============================================================
@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_short', 'updated_at']
    search_fields = ['key', 'description']

    @admin.display(description='値')
    def value_short(self, obj):
        return obj.value[:80]
