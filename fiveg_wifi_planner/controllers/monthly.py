import frappe
from frappe.utils import now_datetime

def monthly_close():
    frappe.logger().info('fiveg_wifi_planner monthly_close ran at ' + str(now_datetime()))