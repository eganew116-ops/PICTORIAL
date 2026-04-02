from django.contrib import admin

from .models import Job, PricingRule


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "job_date",
        "job_code",
        "machine_type",
        "job_type",
        "operator_name",
        "good_qty",
        "reject_qty",
        "total_price",
    )
    list_filter = ("machine_type", "job_type", "qc_status", "job_date")
    search_fields = ("job_code", "material", "operator_name", "notes")
    ordering = ("-job_date", "-id")


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = (
        "machine_type",
        "job_type",
        "price_mode",
        "price_value",
        "is_active",
        "created_at",
    )
    list_filter = ("machine_type", "job_type", "is_active")
    search_fields = ("machine_type", "job_type")
    ordering = ("-created_at", "-id")
