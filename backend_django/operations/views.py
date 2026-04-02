import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from .forms import JobForm, PricingRuleForm
from .models import Job, PricingRule


class OpsLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class OpsLogoutView(LogoutView):
    next_page = "login"


def healthcheck(request):
    return HttpResponse("ok", content_type="text/plain")


def _normalize_machine_type(machine_type):
    machine_type = (machine_type or "").upper()
    if machine_type in {Job.MACHINE_LASER, Job.MACHINE_UV}:
        return machine_type
    return None


def _range_filter(queryset, range_value):
    today = timezone.localdate()

    if range_value == "month":
        return queryset.filter(
            job_date__year=today.year,
            job_date__month=today.month,
        )
    if range_value == "today":
        return queryset.filter(job_date=today)
    return queryset


def _job_filters(queryset, range_value, search_query=""):
    queryset = _range_filter(queryset, range_value)
    search_query = (search_query or "").strip()

    if search_query:
        queryset = queryset.filter(
            Q(job_code__icontains=search_query)
            | Q(material__icontains=search_query)
            | Q(operator_name__icontains=search_query)
            | Q(notes__icontains=search_query),
        )

    return queryset


def _summary_for_queryset(queryset):
    aggregated = queryset.aggregate(
        good=Sum("good_qty"),
        reject=Sum("reject_qty"),
        downtime=Sum("downtime_seconds"),
        revenue=Sum("total_price"),
    )
    return {
        "jobs": queryset.count(),
        "good": aggregated["good"] or 0,
        "reject": aggregated["reject"] or 0,
        "downtime": aggregated["downtime"] or 0,
        "revenue": aggregated["revenue"] or 0,
    }


@login_required
def home(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    range_value = request.GET.get("range", "today")
    jobs = _job_filters(Job.objects.all(), range_value)

    laser_jobs = jobs.filter(machine_type=Job.MACHINE_LASER)
    uv_jobs = jobs.filter(machine_type=Job.MACHINE_UV)

    context = {
        "range_value": range_value,
        "laser_summary": _summary_for_queryset(laser_jobs),
        "uv_summary": _summary_for_queryset(uv_jobs),
        "recent_jobs": jobs[:8],
        "active_pricing_count": PricingRule.objects.filter(is_active=True).count(),
    }
    return render(request, "operations/dashboard.html", context)


@login_required
def job_list(request, machine_type):
    machine_type = _normalize_machine_type(machine_type)
    if not machine_type:
        return redirect("dashboard")

    range_value = request.GET.get("range", "today")
    search_query = request.GET.get("q", "").strip()
    jobs = _job_filters(
        Job.objects.filter(machine_type=machine_type),
        range_value,
        search_query,
    )

    context = {
        "machine_type": machine_type,
        "range_value": range_value,
        "search_query": search_query,
        "jobs": jobs,
        "summary": _summary_for_queryset(jobs),
    }
    return render(request, "operations/job_list.html", context)


@login_required
def job_create(request, machine_type):
    machine_type = _normalize_machine_type(machine_type)
    if not machine_type:
        return redirect("dashboard")

    if request.method == "POST":
        form = JobForm(request.POST, user=request.user, machine_type=machine_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Job berhasil disimpan.")
            return redirect("job_list", machine_type=machine_type.lower())
    else:
        form = JobForm(
            initial={"machine_type": machine_type, "job_date": timezone.localdate()},
            user=request.user,
            machine_type=machine_type,
        )

    return render(
        request,
        "operations/job_form.html",
        {"form": form, "machine_type": machine_type, "page_title": f"Input Job {machine_type}"},
    )


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == "POST":
        form = JobForm(
            request.POST,
            instance=job,
            user=request.user,
            machine_type=job.machine_type,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Job berhasil diupdate.")
            return redirect("job_list", machine_type=job.machine_type.lower())
    else:
        form = JobForm(
            instance=job,
            user=request.user,
            machine_type=job.machine_type,
        )

    return render(
        request,
        "operations/job_form.html",
        {
            "form": form,
            "machine_type": job.machine_type,
            "page_title": f"Edit Job {job.job_code}",
            "job": job,
        },
    )


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    machine_type = job.machine_type.lower()

    if request.method == "POST":
        job.delete()
        messages.success(request, "Job berhasil dihapus.")
    return redirect("job_list", machine_type=machine_type)


@login_required
def job_export_csv(request, machine_type):
    machine_type = _normalize_machine_type(machine_type)
    if not machine_type:
        return redirect("dashboard")

    range_value = request.GET.get("range", "today")
    search_query = request.GET.get("q", "").strip()
    jobs = _job_filters(
        Job.objects.filter(machine_type=machine_type),
        range_value,
        search_query,
    )

    filename = (
        f"{slugify(machine_type)}-{slugify(range_value)}-"
        f"{timezone.localdate().isoformat()}.csv"
    )
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(
        [
            "Tanggal",
            "Job ID",
            "Machine",
            "Job Type",
            "Operator",
            "Material",
            "Durasi (s)",
            "Downtime (s)",
            "Good",
            "Reject",
            "QC Status",
            "Total Price",
            "Catatan",
        ],
    )

    for job in jobs:
        writer.writerow(
            [
                job.job_date.isoformat(),
                job.job_code,
                job.machine_type,
                job.job_type,
                job.operator_name,
                job.material,
                job.actual_seconds,
                job.downtime_seconds,
                job.good_qty,
                job.reject_qty,
                job.qc_status,
                job.total_price or "",
                job.notes,
            ],
        )

    return response


@login_required
def pricing_list(request):
    rules = PricingRule.objects.all()
    return render(
        request,
        "operations/pricing_list.html",
        {
            "rules": rules,
            "active_rules_count": rules.filter(is_active=True).count(),
        },
    )


@login_required
def pricing_create(request):
    if request.method == "POST":
        form = PricingRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pricing rule berhasil disimpan.")
            return redirect("pricing_list")
    else:
        form = PricingRuleForm()
    return render(
        request,
        "operations/pricing_form.html",
        {"form": form, "page_title": "Tambah Pricing Rule"},
    )


@login_required
def pricing_edit(request, pk):
    rule = get_object_or_404(PricingRule, pk=pk)
    if request.method == "POST":
        form = PricingRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, "Pricing rule berhasil diupdate.")
            return redirect("pricing_list")
    else:
        form = PricingRuleForm(instance=rule)
    return render(
        request,
        "operations/pricing_form.html",
        {"form": form, "page_title": f"Edit Pricing Rule #{rule.pk}"},
    )
