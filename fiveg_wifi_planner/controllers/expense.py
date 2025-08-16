import frappe
from frappe.utils import flt, now_datetime, getdate

def on_submit_expense(doc, method):
    # Push expense to ledger (negative amount)
    last = frappe.get_all('Company Ledger', fields=['name','balance_after'], order_by='creation desc', limit=1)
    old_bal = flt(last[0].balance_after) if last else 0
    new_bal = old_bal - flt(doc.amount)
    frappe.get_doc({
        'doctype':'Company Ledger',
        'posting_datetime': now_datetime(),
        'entry_type': 'Expense',
        'reference_doctype': 'Expense',
        'reference_name': doc.name,
        'amount': -flt(doc.amount),
        'balance_after': flt(new_bal),
        'remarks': doc.get('remarks') or ''
    }).insert(ignore_permissions=True)

    # monthly summary: add expense, recompute net
    month = getdate(doc.expense_date).strftime('%Y-%m')
    ms = frappe.get_all('Monthly Summary', filters={'month': month}, limit=1)
    if ms:
        ms_doc = frappe.get_doc('Monthly Summary', ms[0].name)
    else:
        ms_doc = frappe.get_doc({'doctype':'Monthly Summary','month':month,'collected_cash':0,'collected_bank':0,'received_cash':0,'received_bank':0,'total_expense':0,'net_profit':0})
    ms_doc.total_expense = flt(ms_doc.total_expense) + flt(doc.amount)
    ms_doc.net_profit = flt(ms_doc.received_cash) + flt(ms_doc.received_bank) - flt(ms_doc.total_expense)
    ms_doc.save(ignore_permissions=True)