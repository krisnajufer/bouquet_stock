# Copyright (c) 2026, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaterialStock(Document):
	pass

@frappe.whitelist()
def get_critical_stock():
    return frappe.db.sql("""
        SELECT
            material,
            actual_qty,
            `min`
        FROM `tabMaterial Stock`
        WHERE actual_qty <= `min`
    """, as_dict=True)