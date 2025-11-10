from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "first_name", "last_name", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["password", "created_at", "updated_at"]
    ordering = ["-created_at"]
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("email", "first_name", "last_name")
        }),
        ("Системная информация", {
            "fields": ("password", "created_at", "updated_at")
        }),
    )
