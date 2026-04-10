from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BranchForm
from .models import Branch


def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return wrapper
    return decorator


@login_required
@group_required('ADMIN')
def branch_list(request):
    search = request.GET.get('search', '').strip()

    branches = Branch.objects.all().order_by('branch_name')

    if search:
        branches = branches.filter(branch_name__icontains=search)

    return render(request, 'masters/branch_list.html', {
        'branches': branches,
        'search': search,
    })


@login_required
@group_required('ADMIN')
def branch_create(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch created successfully.')
            return redirect('branch_list')
    else:
        form = BranchForm()

    return render(request, 'masters/branch_form.html', {
        'form': form,
        'page_title': 'Create Branch'
    })


@login_required
@group_required('ADMIN')
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully.')
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)

    return render(request, 'masters/branch_form.html', {
        'form': form,
        'page_title': 'Edit Branch',
        'branch': branch,
    })