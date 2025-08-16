import frappe
from frappe.utils import flt, getdate
from .utils import get_or_create

def _update_monthly_collected(doc):
    month = getdate(doc.payment_date).strftime('%Y-%m')
    ms = frappe.get_all('Monthly Summary', filters={'month': month}, limit=1)
    if ms:
        ms_doc = frappe.get_doc('Monthly Summary', ms[0].name)
    else:
        ms_doc = frappe.get_doc({'doctype':'Monthly Summary','month':month,'collected_cash':0,'collected_bank':0,'received_cash':0,'received_bank':0,'total_expense':0,'net_profit':0})
    if doc.payment_type == 'Cash':
        ms_doc.collected_cash = flt(ms_doc.collected_cash) + flt(doc.amount)
    else:
        ms_doc.collected_bank = flt(ms_doc.collected_bank) + flt(doc.amount)
    ms_doc.net_profit = flt(ms_doc.received_cash) + flt(ms_doc.received_bank) - flt(ms_doc.total_expense)
    ms_doc.save(ignore_permissions=True)

def validate_payment_permission(doc, method):
    user = frappe.session.user
    roles = frappe.get_roles(user)
    if 'Staff' in roles and not doc.get('__islocal'):
        frappe.throw('Staff users cannot edit existing payments')
    if flt(doc.amount) <= 0:
        frappe.throw('Amount must be greater than zero')

def before_delete_payment(doc, method):
    roles = frappe.get_roles(frappe.session.user)
    if 'Staff' in roles:
        frappe.throw('Staff users cannot delete payments')

def on_submit_payment(doc, method):
    # reduce customer balance on collection
    if doc.customer:
        cust = frappe.get_doc('Customer', doc.customer)
        cust.balance_total = flt(cust.get('balance_total') or 0) - flt(doc.amount)
        cust.save(ignore_permissions=True)
    # bump monthly collected
    _update_monthly_collected(doc)