import frappe
def get_or_create(doctype, filters=None, **doc):
    existing = None
    if filters:
        existing = frappe.get_all(doctype, filters=filters, limit=1)
    if existing:
        return frappe.get_doc(doctype, existing[0].name)
    d = frappe.get_doc(doc)
    d.insert(ignore_permissions=True)
    return d