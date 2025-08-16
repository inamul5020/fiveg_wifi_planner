import frappe
from frappe.utils import now_datetime, getdate

# ----------------------
# Base Setup (safe at install time)
# ----------------------
def _ensure_module():
    if not frappe.db.exists("Module Def", "Fiveg Wifi Planner"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Fiveg Wifi Planner",
            "app_name": "fiveg_wifi_planner"
        }).insert(ignore_permissions=True)


def _ensure_roles():
    for r in ["Manager", "Staff"]:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": r
            }).insert(ignore_permissions=True)


def _ensure_workspace():
    if not frappe.db.exists("Workspace", "Fiveg Wifi Planner"):
        frappe.get_doc({
            "doctype": "Workspace",
            "workspace_name": "Fiveg Wifi Planner",
            "label": "Fiveg Wifi Planner",
            "title": "Fiveg Wifi Planner",
            "public": 1,
            "module": "Fiveg Wifi Planner",
            "content": "[]"
        }).insert(ignore_permissions=True)


# ----------------------
# Number Cards
# ----------------------
def _create_number_cards():
    def make(label, doctype, function="Sum", field=None, filters=None):
        if frappe.db.exists("Number Card", label):
            return
        if not frappe.db.exists("DocType", doctype):
            frappe.log_error(f"Skipping card {label} — missing DocType {doctype}")
            return

        nd = {
            "doctype": "Number Card",
            "label": label,
            "function": function,
            "document_type": doctype,
            "filters_json": frappe.as_json(filters or {}),
            "is_public": 1
        }
        if field:
            nd["aggregate_function_based_on"] = field
        frappe.get_doc(nd).insert(ignore_permissions=True)

    make("Pending Handover (QAR)", "Customer Payment", "Sum", "amount", {"company_received": 0})
    make("Collected (Received) Cash (QAR)", "Monthly Summary", "Sum", "received_cash", {})
    make("Collected (Received) Bank (QAR)", "Monthly Summary", "Sum", "received_bank", {})
    make("Total Expense (QAR)", "Monthly Summary", "Sum", "total_expense", {})
    make("Net Profit (QAR)", "Monthly Summary", "Sum", "net_profit", {})


# ----------------------
# Demo Data
# ----------------------
def _demo_data():
    required = ["Customer Department", "ABR Package", "Customer",
                "Customer Payment", "Staff Payment Submission", "Expense"]
    for dt in required:
        if not frappe.db.exists("DocType", dt):
            frappe.log_error(f"Skipping demo data — missing DocType {dt}")
            return

    # Departments
    if not frappe.db.exists("Customer Department", "Sales"):
        frappe.get_doc({"doctype": "Customer Department", "department_name": "Sales"}).insert(ignore_permissions=True)
    if not frappe.db.exists("Customer Department", "Support"):
        frappe.get_doc({"doctype": "Customer Department", "department_name": "Support"}).insert(ignore_permissions=True)

    # Packages
    if not frappe.db.exists("ABR Package", "Basic 50Mbps"):
        frappe.get_doc({"doctype": "ABR Package", "package_name": "Basic 50Mbps", "price": 200.0, "speed": "50Mbps", "validity_days": 30}).insert(ignore_permissions=True)
    if not frappe.db.exists("ABR Package", "Pro 100Mbps"):
        frappe.get_doc({"doctype": "ABR Package", "package_name": "Pro 100Mbps", "price": 300.0, "speed": "100Mbps", "validity_days": 30}).insert(ignore_permissions=True)

    # Customers
    if not frappe.db.exists("Customer", "CUST-0001"):
        frappe.get_doc({"doctype": "Customer", "customer_id": "CUST-0001", "customer_name": "Ali Hassan", "department": "Sales", "package": "Basic 50Mbps", "balance_total": 0}).insert(ignore_permissions=True)
    if not frappe.db.exists("Customer", "CUST-0002"):
        frappe.get_doc({"doctype": "Customer", "customer_id": "CUST-0002", "customer_name": "Mohamed Kareem", "department": "Support", "package": "Pro 100Mbps", "balance_total": 0}).insert(ignore_permissions=True)

    # Payments
    if not frappe.get_all("Customer Payment", filters={"customer": "CUST-0001"}, limit=1):
        p = frappe.get_doc({
            "doctype": "Customer Payment",
            "customer": "CUST-0001",
            "amount": 500.0,
            "payment_type": "Cash",
            "payment_date": getdate(now_datetime()),
            "collected_by": frappe.session.user,
            "remarks": "Demo cash collection"
        })
        p.insert(ignore_permissions=True).submit()

    # Staff submission
    if not frappe.get_all("Staff Payment Submission"):
        cp = frappe.get_all("Customer Payment", filters={"company_received": 0}, limit=1)
        if cp:
            sub = frappe.get_doc({
                "doctype": "Staff Payment Submission",
                "staff_user": frappe.session.user,
                "submission_date": now_datetime(),
                "payments": [{
                    "doctype": "Staff Payment Submission Item",
                    "customer_payment": cp[0].name,
                    "amount": 500.0
                }]
            }).insert(ignore_permissions=True)
            sub.submit()

    # Expense
    if not frappe.get_all("Expense"):
        e = frappe.get_doc({
            "doctype": "Expense",
            "expense_date": getdate(now_datetime()),
            "expense_type": "ISP",
            "amount": 200.0,
            "remarks": "Demo ISP fee"
        }).insert(ignore_permissions=True)
        e.submit()


# ----------------------
# Hooks entry points
# ----------------------
def basic_setup():
    """Runs at install time (safe stuff only)."""
    frappe.clear_cache()
    _ensure_module()
    _ensure_roles()
    _ensure_workspace()
    frappe.db.commit()


def post_migrate_setup():
    """Runs after migrate when all doctypes are present."""
    frappe.clear_cache()
    _create_number_cards()
    _demo_data()
    frappe.db.commit()
