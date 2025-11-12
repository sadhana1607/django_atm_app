from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import PinForm, WithdrawForm, DepositForm
from django.contrib import messages

CORRECT_PIN = 1234
INITIAL_BALANCE = 10000
MAX_ATTEMPTS = 3

def ensure_session(request):
    if 'attempts' not in request.session:
        request.session['attempts'] = 0
    if 'blocked' not in request.session:
        request.session['blocked'] = False
    if 'authenticated' not in request.session:
        request.session['authenticated'] = False
    if 'balance' not in request.session:
        request.session['balance'] = INITIAL_BALANCE

def pin_entry(request):
    ensure_session(request)
    if request.session.get('blocked'):
        return render(request, 'atm_app/blocked.html')

    if request.method == 'POST':
        form = PinForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            if pin == CORRECT_PIN:
                request.session['authenticated'] = True
                request.session['attempts'] = 0
                return redirect('atm_app:dashboard')
            else:
                request.session['attempts'] += 1
                remaining = MAX_ATTEMPTS - request.session['attempts']
                if request.session['attempts'] >= MAX_ATTEMPTS:
                    request.session['blocked'] = True
                    return render(request, 'atm_app/blocked.html')
                messages.error(request, f'Invalid PIN — {remaining} attempt(s) left')
    else:
        form = PinForm()
    return render(request, 'atm_app/index.html', {'form': form})

def dashboard(request):
    ensure_session(request)
    if not request.session.get('authenticated'):
        return redirect('atm_app:pin_entry')

    balance = request.session.get('balance', INITIAL_BALANCE)
    wform = WithdrawForm()
    dform = DepositForm()

    if request.method == 'POST':
        if 'withdraw' in request.POST:
            wform = WithdrawForm(request.POST)
            if wform.is_valid():
                amt = wform.cleaned_data['amount']
                if amt > balance:
                    messages.error(request, 'Insufficient balance')
                else:
                    balance -= amt
                    request.session['balance'] = balance
                    messages.success(request, f'Withdrawn {amt}. New balance: {balance}')
                    return redirect(reverse('atm_app:dashboard'))
        elif 'deposit' in request.POST:
            dform = DepositForm(request.POST)
            if dform.is_valid():
                amt = dform.cleaned_data['amount']
                balance += amt
                request.session['balance'] = balance
                messages.success(request, f'Deposited {amt}. New balance: {balance}')
                return redirect(reverse('atm_app:dashboard'))

    return render(request, 'atm_app/dashboard.html', {'balance': balance, 'wform': wform, 'dform': dform})

def user_logout(request):
    request.session.flush()
    return redirect('atm_app:pin_entry')
