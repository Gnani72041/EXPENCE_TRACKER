from django.shortcuts import render, redirect
from .models import TrackingHistory, CurrentBalance
from django.db.models import Sum, F, Case, When, FloatField


def index(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        amount_str = request.POST.get('amount')

        # Handle empty input
        if not description or amount_str == '':
            return redirect('/')

        raw_amount = float(amount_str)
        expense_type = 'CREDIT' if raw_amount >= 0 else 'DEBIT'
        amount = abs(raw_amount)

        current_balance, _ = CurrentBalance.objects.get_or_create(id=1)

        # Save transaction with POSITIVE amount
        TrackingHistory.objects.create(
            amount=amount,
            expense_type=expense_type,
            current_balance=current_balance,
            description=description
        )

        # ✅ Recalculate balance = CREDIT - DEBIT with output_field specified
        total = TrackingHistory.objects.aggregate(
            balance=Sum(
                Case(
                    When(expense_type='CREDIT', then=F('amount')),
                    When(expense_type='DEBIT', then=-F('amount')),
                    default=0,
                    output_field=FloatField()
                )
            )
        )['balance'] or 0.0

        current_balance.current_balance = total
        current_balance.save()

        return redirect('/')

    current_balance, _ = CurrentBalance.objects.get_or_create(id=1)

    income = TrackingHistory.objects.filter(expense_type='CREDIT').aggregate(
        total=Sum('amount'))['total'] or 0

    expense = TrackingHistory.objects.filter(expense_type='DEBIT').aggregate(
        total=Sum('amount'))['total'] or 0

    context = {
        'income': income,
        'expense': expense,
        'transactions': TrackingHistory.objects.all(),
        'current_balance': current_balance
    }

    return render(request, "index.html", context)


def delete_transaction(request, id):
    transaction = TrackingHistory.objects.filter(id=id).first()
    if transaction:
        transaction.delete()

        current_balance, _ = CurrentBalance.objects.get_or_create(id=1)

        # ✅ Recalculate balance with output_field specified
        total = TrackingHistory.objects.aggregate(
            balance=Sum(
                Case(
                    When(expense_type='CREDIT', then=F('amount')),
                    When(expense_type='DEBIT', then=-F('amount')),
                    default=0,
                    output_field=FloatField()
                )
            )
        )['balance'] or 0.0

        current_balance.current_balance = total
        current_balance.save()

    return redirect('/')
