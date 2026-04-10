from django.db.models import Count
from django.shortcuts import render
from request_app.models import ShareholderGiftRequest
from master_app.models import BranchMaster


def report_summary_view(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    branch_id = request.GET.get("branch_id")

    qs = ShareholderGiftRequest.objects.select_related(
        "branch",
        "shareholder",
        "gift_item"
    ).all().order_by("-id")

    if from_date:
        qs = qs.filter(insert_date__date__gte=from_date)
    if to_date:
        qs = qs.filter(insert_date__date__lte=to_date)
    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    status_summary = {
        "inserted": qs.count(),
        "accepted": qs.filter(status="Accepted").count(),
        "rejected": qs.filter(status="Rejected").count(),
        "shipped": qs.filter(status="Shipped").count(),
        "delivered": qs.filter(status="Delivered").count(),
    }

    branch_summary = (
        qs.values("branch__branch_name")
        .annotate(inserted=Count("id"))
        .order_by("branch__branch_name")
    )

    branch_queryset = BranchMaster.objects.all().order_by("branch_name")

    context = {
        "from_date": from_date,
        "to_date": to_date,
        "branch_id": branch_id,
        "branch_queryset": branch_queryset,
        "status_summary": status_summary,
        "branch_summary": branch_summary,
        "details": qs,   # pass full queryset, not values()
    }

    return render(request, "report_summary.html", context)