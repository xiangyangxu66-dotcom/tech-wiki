from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from .models import Category, Note


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['id', 'name', 'slug', 'parent', 'note_count']
    search_fields = ['name', 'slug']
    readonly_fields = ['slug']
    list_select_related = ['parent']

    @admin.display(description='ノート数')
    def note_count(self, obj):
        return obj.notes.count()


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'bookmark_icon', 'status',
                    'category_link', 'tag_display', 'updated_at']
    list_filter = ['category', 'status', 'bookmark', 'created_at']
    search_fields = ['title', 'slug', 'content']
    readonly_fields = ['slug', 'note_tags', 'created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    ordering = ['-bookmark', '-updated_at']
    list_select_related = ['category']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content')
        }),
        ('ステータス', {
            'fields': ('status', 'bookmark'),
        }),
        ('カテゴリとタグ', {
            'fields': ('category', 'note_tags'),
        }),
        ('日時', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='★', boolean=True)
    def bookmark_icon(self, obj):
        return obj.bookmark

    @admin.display(description='カテゴリ')
    def category_link(self, obj):
        if obj.category:
            url = f'/admin/wiki/category/{obj.category.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'

    @admin.display(description='タグ')
    def tag_display(self, obj):
        return ', '.join(obj.note_tags or [])
