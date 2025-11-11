from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Shift
from .forms import ShiftForm
from apps.user_authentication.models import CustomUser  # ✅ Correct import

@login_required
def shift_list(request):
    if request.user.role == 'shift_manager':
        shifts = Shift.objects.filter(manager=request.user)
    else:
        shifts = Shift.objects.all()
    return render(request, 'shift_management/shift_list.html', {'shifts': shifts})

@login_required
def create_shift(request):
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.manager = request.user
            shift.save()
            return redirect('shift_list')
    else:
        form = ShiftForm()
    return render(request, 'shift_management/create_shift.html', {'form': form})
