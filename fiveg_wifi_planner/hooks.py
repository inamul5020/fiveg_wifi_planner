app_name = "fiveg_wifi_planner"
app_title = "5G Wifi Planner"
app_publisher = "Generated"
app_description = "Payment tracking, company ledger, reconciliation and dashboard for 5G Wifi Planner"
app_email = "dev@example.com"
app_license = "MIT"

# ----------------------
# Run only core scaffolding at install
# ----------------------
after_install = "fiveg_wifi_planner.install.basic_setup"

# ----------------------
# Run Number Cards + Demo Data safely AFTER migrations
# ----------------------
after_migrate = [
    "fiveg_wifi_planner.install.post_migrate_setup"
]

# ----------------------
# DocEvents (your controllers)
# ----------------------
doc_events = {
    "Customer Payment": {
        "validate": "fiveg_wifi_planner.controllers.customer_payment.validate_payment_permission",
        "before_delete": "fiveg_wifi_planner.controllers.customer_payment.before_delete_payment",
        "on_submit": "fiveg_wifi_planner.controllers.customer_payment.on_submit_payment"
    },
    "Staff Payment Submission": {
        "validate": "fiveg_wifi_planner.controllers.staff_submission.validate_submission",
        "before_submit": "fiveg_wifi_planner.controllers.staff_submission.on_before_submit_auto_approve",
        "on_submit": "fiveg_wifi_planner.controllers.staff_submission.on_submit_finalize"
    },
    "Expense": {
        "on_submit": "fiveg_wifi_planner.controllers.expense.on_submit_expense"
    }
}
scheduler_events = {"monthly": ["fiveg_wifi_planner.controllers.monthly.monthly_close"]}