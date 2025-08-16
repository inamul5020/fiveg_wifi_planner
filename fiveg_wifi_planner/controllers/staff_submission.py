import frappe
from frappe.utils import flt, now_datetime, getdate
from .utils import get_or_create

def _touch_monthly(doc, delta_cash=0, delta_bank=0):
    # Use first linked payment to infer month, fallback to current month
    month = None
    for it in doc.get('payments') or []:
        p = frappe.get_doc('Customer Payment', it.customer_payment)
        month = getdate(p.payment_date).strftime('%Y-%m')
        break
    if not month:
        month = getdate(now_datetime()).strftime('%Y-%m')

    ms = frappe.get_all('Monthly Summary', filters={'month': month}, limit=1)
    if ms:
        ms_doc = frappe.get_doc('Monthly Summary', ms[0].name)
    else:
        ms_doc = frappe.get_doc({'doctype':'Monthly Summary','month':month,'collected_cash':0,'collected_bank':0,'received_cash':0,'received_bank':0,'total_expense':0,'net_profit':0})
    ms_doc.received_cash = flt(ms_doc.received_cash) + flt(delta_cash)
    ms_doc.received_bank = flt(ms_doc.received_bank) + flt(delta_bank)
    ms_doc.net_profit = flt(ms_doc.received_cash) + flt(ms_doc.received_bank) - flt(ms_doc.total_expense)
    ms_doc.save(ignore_permissions=True)

def _post_ledger(amount, ref_doctype, ref_name, remarks=None):
    last = frappe.get_all('Company Ledger', fields=['name','balance_after'], order_by='creation desc', limit=1)
    old_bal = flt(last[0].balance_after) if last else 0
    new_bal = old_bal + flt(amount)
    led = frappe.get_doc({
        'doctype':'Company Ledger',
        'posting_datetime': now_datetime(),
        'entry_type': 'Income' if amount >=0 else 'Expense',
        'reference_doctype': ref_doctype,
        'reference_name': ref_name,
        'amount': flt(amount),
        'balance_after': flt(new_bal),
        'remarks': remarks or ''
    }).insert(ignore_permissions=True)
    return led

def validate_submission(doc, method):
    if not doc.get('payments'):
        frappe.throw('Add at least one collected Customer Payment to hand over')
    total = 0
    for it in doc.get('payments'):
        p = frappe.get_doc('Customer Payment', it.customer_payment)
        if p.company_received:
            frappe.throw(f'Payment {p.name} already received by company')
        total += flt(p.amount)
    doc.total_amount = total

def on_before_submit_auto_approve(doc, method):
    # set approval fields before submit to avoid modifying submitted doc
    doc.status = 'Approved'
    doc.approved_by = frappe.session.user
    doc.approved_on = now_datetime()

def on_submit_finalize(doc, method):
    # mark payments as received and push to ledger
    cash = 0
    bank = 0
    for it in doc.get('payments'):
        p = frappe.get_doc('Customer Payment', it.customer_payment)
        p.company_received = 1
        p.is_handover_submitted = 1
        p.handover_submission = doc.name
        p.save(ignore_permissions=True)

        if p.payment_type == 'Cash':
            cash += flt(p.amount)
        else:
            bank += flt(p.amount)

        _post_ledger(flt(p.amount), 'Customer Payment', p.name,
                     remarks='Handover approved via Staff Submission ' + doc.name)

    _touch_monthly(doc, delta_cash=cash, delta_bank=bank)