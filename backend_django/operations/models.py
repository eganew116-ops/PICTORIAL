from decimal import Decimal

from django.db import models


class PricingRule(models.Model):
    MACHINE_LASER = "LASER"
    MACHINE_UV = "UV"
    MACHINE_CHOICES = [
        (MACHINE_LASER, "Laser"),
        (MACHINE_UV, "UV"),
    ]

    MODE_PER_MINUTE = "per_minute"
    MODE_PER_PIECE = "per_piece"
    MODE_PER_JOB = "per_job"
    PRICE_MODE_CHOICES = [
        (MODE_PER_MINUTE, "Per Menit"),
        (MODE_PER_PIECE, "Per Pcs"),
        (MODE_PER_JOB, "Per Job"),
    ]

    JOB_TYPE_CHOICES = [
        ("CUT", "CUT"),
        ("ENGRAVE", "ENGRAVE"),
        ("COMBO", "COMBO"),
        ("PRINT", "PRINT"),
    ]

    machine_type = models.CharField(max_length=20, choices=MACHINE_CHOICES)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    price_mode = models.CharField(
        max_length=20,
        choices=PRICE_MODE_CHOICES,
        blank=True,
        null=True,
    )
    price_value = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Pricing Rule"
        verbose_name_plural = "Pricing Rules"

    def __str__(self):
        return f"{self.machine_type} - {self.job_type} - {self.price_value}"


class Job(models.Model):
    MACHINE_LASER = PricingRule.MACHINE_LASER
    MACHINE_UV = PricingRule.MACHINE_UV
    MACHINE_CHOICES = PricingRule.MACHINE_CHOICES
    JOB_TYPE_CHOICES = PricingRule.JOB_TYPE_CHOICES
    PRICE_MODE_CHOICES = PricingRule.PRICE_MODE_CHOICES

    QC_OK = "OK"
    QC_REWORK = "REWORK"
    QC_HOLD = "HOLD"
    QC_STATUS_CHOICES = [
        (QC_OK, "OK"),
        (QC_REWORK, "REWORK"),
        (QC_HOLD, "HOLD"),
    ]

    job_code = models.CharField(max_length=255)
    operator_name = models.CharField(max_length=255)
    machine_type = models.CharField(max_length=20, choices=MACHINE_CHOICES)
    job_date = models.DateField()
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    material = models.CharField(max_length=255)
    thickness_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    color = models.CharField(max_length=255, blank=True)
    preset = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    actual_seconds = models.PositiveIntegerField(default=0)
    downtime_seconds = models.PositiveIntegerField(default=0)
    actual_minutes = models.PositiveIntegerField(default=0)
    downtime_minutes = models.PositiveIntegerField(default=0)
    qty_pcs = models.PositiveIntegerField(default=0)
    good_qty = models.PositiveIntegerField(default=0)
    reject_qty = models.PositiveIntegerField(default=0)
    reject_reasons = models.JSONField(blank=True, default=list)
    qc_status = models.CharField(
        max_length=50,
        choices=QC_STATUS_CHOICES,
        default=QC_OK,
    )
    notes = models.TextField(blank=True)
    price_mode = models.CharField(max_length=20, blank=True)
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-job_date", "-id"]

    def __str__(self):
        return f"{self.machine_type} - {self.job_code}"

    @property
    def revenue_value(self):
        return self.total_price or Decimal("0")
