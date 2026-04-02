from datetime import datetime, time, timedelta
from decimal import Decimal

from django import forms
from django.utils import timezone

from .models import Job, PricingRule

REJECT_REASON_CHOICES = [
    ("Gosong/Burn mark", "Gosong/Burn mark"),
    ("Tidak tembus", "Tidak tembus"),
    ("Meleleh", "Meleleh"),
    ("Dimensi meleset", "Dimensi meleset"),
    ("Pecah/retak", "Pecah/retak"),
    ("Masking rusak", "Masking rusak"),
    ("Lainnya", "Lainnya"),
]


class PricingRuleForm(forms.ModelForm):
    class Meta:
        model = PricingRule
        fields = [
            "machine_type",
            "job_type",
            "price_mode",
            "price_value",
            "is_active",
        ]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("machine_type") == PricingRule.MACHINE_LASER:
            cleaned_data["price_mode"] = PricingRule.MODE_PER_MINUTE
            self.cleaned_data["price_mode"] = PricingRule.MODE_PER_MINUTE
        return cleaned_data


class JobForm(forms.ModelForm):
    SOURCE_PICTORIAL = "PICTORIAL"
    SOURCE_CUSTOMER = "CUSTOMER"
    SOURCE_CHOICES = [
        (SOURCE_PICTORIAL, "Bahan dari Pictorial"),
        (SOURCE_CUSTOMER, "Bahan dari Customer"),
    ]

    reject_reasons = forms.MultipleChoiceField(
        choices=REJECT_REASON_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    laser_material_source = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        required=False,
    )

    class Meta:
        model = Job
        fields = [
            "job_code",
            "machine_type",
            "job_date",
            "job_type",
            "material",
            "thickness_mm",
            "color",
            "preset",
            "qty_pcs",
            "actual_seconds",
            "downtime_seconds",
            "good_qty",
            "reject_qty",
            "reject_reasons",
            "qc_status",
            "notes",
        ]
        widgets = {
            "job_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "machine_type": forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, machine_type=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        effective_machine_type = (
            machine_type
            or self.initial.get("machine_type")
            or getattr(self.instance, "machine_type", Job.MACHINE_LASER)
        )

        self.fields["machine_type"].initial = effective_machine_type
        self.fields["job_date"].initial = self.initial.get(
            "job_date",
        ) or timezone.localdate()
        self.fields["reject_reasons"].initial = self.instance.reject_reasons

        if effective_machine_type == Job.MACHINE_UV:
            self.fields["job_type"].choices = [("PRINT", "PRINT")]
            self.fields["job_type"].initial = "PRINT"
            self.fields["qty_pcs"].label = "Qty (pcs)"
            self.fields["laser_material_source"].widget = forms.HiddenInput()
        else:
            self.fields["qty_pcs"].label = "Area Potong"
            initial_source = (
                self.SOURCE_PICTORIAL
                if (getattr(self.instance, "qty_pcs", 0) or 0) > 0
                else self.SOURCE_CUSTOMER
            )
            if not self.instance.pk:
                initial_source = self.SOURCE_PICTORIAL
            self.fields["laser_material_source"].initial = initial_source

    def clean(self):
        cleaned_data = super().clean()
        machine_type = cleaned_data.get("machine_type") or getattr(
            self.instance,
            "machine_type",
            Job.MACHINE_LASER,
        )
        reject_qty = cleaned_data.get("reject_qty") or 0
        reject_reasons = cleaned_data.get("reject_reasons") or []
        qty_pcs = cleaned_data.get("qty_pcs") or 0

        if machine_type == Job.MACHINE_UV:
            cleaned_data["job_type"] = "PRINT"
        else:
            source = cleaned_data.get("laser_material_source") or self.SOURCE_PICTORIAL
            if source == self.SOURCE_CUSTOMER:
                cleaned_data["qty_pcs"] = 0
            elif qty_pcs <= 0:
                self.add_error("qty_pcs", "Area potong wajib diisi (> 0).")

        if reject_qty > 0 and not reject_reasons:
            self.add_error(
                "reject_reasons",
                "Kalau reject > 0, pilih minimal 1 alasan reject.",
            )

        if (cleaned_data.get("actual_seconds") or 0) <= 0:
            self.add_error("actual_seconds", "Durasi mesin wajib > 0.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        machine_type = instance.machine_type
        seconds = instance.actual_seconds or 0
        downtime_seconds = instance.downtime_seconds or 0

        if machine_type == Job.MACHINE_UV:
            instance.job_type = "PRINT"
        else:
            source = self.cleaned_data.get("laser_material_source") or self.SOURCE_PICTORIAL
            if source == self.SOURCE_CUSTOMER:
                instance.qty_pcs = 0

        instance.actual_minutes = round(seconds / 60)
        instance.downtime_minutes = round(downtime_seconds / 60)
        instance.reject_reasons = self.cleaned_data.get("reject_reasons") or []
        instance.operator_name = (
            self.user.get_full_name().strip() or self.user.username
            if self.user and self.user.is_authenticated
            else "Operator"
        )

        now_local = timezone.localtime()
        naive_end = datetime.combine(
            instance.job_date,
            time(now_local.hour, now_local.minute, now_local.second),
        )
        instance.end_time = timezone.make_aware(
            naive_end,
            timezone.get_current_timezone(),
        )
        instance.start_time = instance.end_time - timedelta(seconds=seconds)

        rule = PricingRule.objects.filter(
            is_active=True,
            machine_type=instance.machine_type,
            job_type=instance.job_type,
        ).order_by("-created_at", "-id").first()

        instance.price_mode = ""
        instance.unit_price = None
        instance.total_price = None

        if rule:
            unit_price = rule.price_value
            total_price = Decimal("0")

            if instance.machine_type == Job.MACHINE_LASER:
                minute_cost = unit_price * Decimal(seconds) / Decimal("60")
                total_price = minute_cost + Decimal(instance.qty_pcs or 0)
                instance.price_mode = PricingRule.MODE_PER_MINUTE
            elif rule.price_mode == PricingRule.MODE_PER_MINUTE:
                total_price = unit_price * Decimal(seconds) / Decimal("60")
                instance.price_mode = rule.price_mode
            elif rule.price_mode == PricingRule.MODE_PER_PIECE:
                total_price = unit_price * Decimal(instance.qty_pcs or 0)
                instance.price_mode = rule.price_mode
            elif rule.price_mode == PricingRule.MODE_PER_JOB:
                total_price = unit_price
                instance.price_mode = rule.price_mode

            instance.unit_price = unit_price
            instance.total_price = total_price.quantize(Decimal("0.01"))

        if commit:
            instance.save()

        return instance
