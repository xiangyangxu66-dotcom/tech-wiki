from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, NoteViewSet,
    AuditLogViewSet, SystemConfigViewSet,
    health_check, health_detailed,
    tag_aggregation, tag_list,
)

router = DefaultRouter()
router.register(r'categories',    CategoryViewSet)
router.register(r'notes',         NoteViewSet)
router.register(r'audit-logs',    AuditLogViewSet)
router.register(r'system-configs', SystemConfigViewSet)

urlpatterns = [
    path('health/',          health_check,     name='health-check'),
    path('health/detailed/', health_detailed,  name='health-detailed'),
    path('tags/',            tag_aggregation,  name='tag-aggregation'),
    path('tags/list/',       tag_list,         name='tag-list'),
    path('', include(router.urls)),
]
