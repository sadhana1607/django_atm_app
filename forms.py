from django import forms

class PinForm(forms.Form):
    pin = forms.IntegerField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter PIN'}), label='PIN')

class WithdrawForm(forms.Form):
    amount = forms.IntegerField(min_value=1, label='Withdraw amount')

class DepositForm(forms.Form):
    amount = forms.IntegerField(min_value=0, label='Deposit amount')
