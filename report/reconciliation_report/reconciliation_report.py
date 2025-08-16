import frappe
from frappe.utils import flt

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Staff User","fieldname":"staff_user","fieldtype":"Link","options":"User","width":180},
        {"label":"Payment Type","fieldname":"payment_type","fieldtype":"Data","width":120},
        {"label":"Count","fieldname":"cnt","fieldtype":"Int","width":80},
        {"label":"Pending Amount (QAR)","fieldname":"amount","fieldtype":"Currency","width":160}
    ]

    rows = []
    data = frappe.db.sql("""
        select cp.collected_by as staff_user, cp.payment_type,
               count(1) as cnt, sum(cp.amount) as amount
        from `tabCustomer Payment` cp
        where ifnull(cp.company_received,0)=0
        group by cp.collected_by, cp.payment_type
    """, as_dict=True)

    for d in data:
        rows.append(d)

    total = sum([flt(r.get("amount") or 0) for r in rows])
    rows.append({"staff_user":"TOTAL","payment_type":"-","cnt": sum([r.get("cnt") or 0 for r in rows if isinstance(r.get('cnt'), int)]),"amount": total})
    return columns, rows