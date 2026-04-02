from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Job, PricingRule


class OperationsViewsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="operator",
            password="password",
            first_name="Gani",
            last_name="Operator",
        )
        self.client.force_login(self.user)

    def _create_job(self, **overrides):
        payload = {
            "job_code": "JOB-001",
            "operator_name": "Gani Operator",
            "machine_type": Job.MACHINE_UV,
            "job_date": timezone.localdate(),
            "job_type": "PRINT",
            "material": "Sticker",
            "thickness_mm": None,
            "color": "Full Color",
            "preset": "Preset A",
            "actual_seconds": 120,
            "downtime_seconds": 10,
            "actual_minutes": 2,
            "downtime_minutes": 0,
            "qty_pcs": 3,
            "good_qty": 3,
            "reject_qty": 0,
            "reject_reasons": [],
            "qc_status": Job.QC_OK,
            "notes": "",
            "price_mode": PricingRule.MODE_PER_PIECE,
            "unit_price": Decimal("5000.00"),
            "total_price": Decimal("15000.00"),
        }
        payload.update(overrides)
        return Job.objects.create(**payload)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_uv_job_creation_uses_active_pricing_rule(self):
        PricingRule.objects.create(
            machine_type=PricingRule.MACHINE_UV,
            job_type="PRINT",
            price_mode=PricingRule.MODE_PER_PIECE,
            price_value=Decimal("5000.00"),
            is_active=True,
        )

        response = self.client.post(
            reverse("job_create", kwargs={"machine_type": "uv"}),
            {
                "job_code": "UV-001",
                "machine_type": Job.MACHINE_UV,
                "job_date": timezone.localdate().isoformat(),
                "job_type": "PRINT",
                "material": "Sticker",
                "thickness_mm": "",
                "color": "Full Color",
                "preset": "Preset A",
                "qty_pcs": 3,
                "actual_seconds": 120,
                "downtime_seconds": 0,
                "good_qty": 3,
                "reject_qty": 0,
                "qc_status": Job.QC_OK,
                "notes": "Tes UV",
            },
        )

        self.assertEqual(response.status_code, 302)
        job = Job.objects.get(job_code="UV-001")
        self.assertEqual(job.operator_name, "Gani Operator")
        self.assertEqual(job.job_type, "PRINT")
        self.assertEqual(job.price_mode, PricingRule.MODE_PER_PIECE)
        self.assertEqual(job.total_price, Decimal("15000.00"))
        self.assertEqual(job.actual_minutes, 2)

    def test_laser_customer_material_sets_qty_zero(self):
        PricingRule.objects.create(
            machine_type=PricingRule.MACHINE_LASER,
            job_type="CUT",
            price_mode=PricingRule.MODE_PER_MINUTE,
            price_value=Decimal("60.00"),
            is_active=True,
        )

        response = self.client.post(
            reverse("job_create", kwargs={"machine_type": "laser"}),
            {
                "job_code": "LS-001",
                "machine_type": Job.MACHINE_LASER,
                "job_date": timezone.localdate().isoformat(),
                "job_type": "CUT",
                "material": "Acrylic",
                "thickness_mm": "3",
                "color": "Clear",
                "preset": "Preset B",
                "qty_pcs": 99,
                "actual_seconds": 120,
                "downtime_seconds": 30,
                "good_qty": 1,
                "reject_qty": 0,
                "qc_status": Job.QC_OK,
                "notes": "Tes laser customer",
                "laser_material_source": "CUSTOMER",
            },
        )

        self.assertEqual(response.status_code, 302)
        job = Job.objects.get(job_code="LS-001")
        self.assertEqual(job.qty_pcs, 0)
        self.assertEqual(job.price_mode, PricingRule.MODE_PER_MINUTE)
        self.assertEqual(job.total_price, Decimal("120.00"))
        self.assertEqual(job.downtime_minutes, 0)

    def test_job_list_search_filters_results(self):
        self._create_job(job_code="UV-ALPHA", notes="urgent customer")
        self._create_job(job_code="UV-BETA", material="Banner")

        response = self.client.get(
            reverse("job_list", kwargs={"machine_type": "uv"}),
            {"range": "all", "q": "alpha"},
        )

        self.assertEqual(response.status_code, 200)
        jobs = list(response.context["jobs"])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].job_code, "UV-ALPHA")

    def test_job_export_csv_uses_current_filters(self):
        self._create_job(job_code="UV-EXPORT", notes="siap export")
        self._create_job(job_code="UV-HIDDEN", material="Acrylic")

        response = self.client.get(
            reverse("job_export_csv", kwargs={"machine_type": "uv"}),
            {"range": "all", "q": "export"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        content = response.content.decode("utf-8-sig")
        self.assertIn("UV-EXPORT", content)
        self.assertNotIn("UV-HIDDEN", content)
