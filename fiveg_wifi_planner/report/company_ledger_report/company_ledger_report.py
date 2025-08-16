import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Posting Datetime","fieldname":"posting_datetime","fieldtype":"Datetime","width":180},
        {"label":"Entry Type","fieldname":"entry_type","fieldtype":"Data","width":100},
        {"label":"Reference","fieldname":"reference","fieldtype":"Data","width":220},
        {"label":"Amount (QAR)","fieldname":"amount","fieldtype":"Currency","width":140},
        {"label":"Balance After (QAR)","fieldname":"balance_after","fieldtype":"Currency","width":160},
        {"label":"Remarks","fieldname":"remarks","fieldtype":"Small Text","width":220}
    ]

    data = frappe.db.sql("""
        select posting_datetime, entry_type,
               concat(reference_doctype, ' / ', reference_name) as reference,
               amount, balance_after, remarks
        from `tabCompany Ledger`
        order by posting_datetime asc, creation asc
    """, as_dict=True)

    return columns, data