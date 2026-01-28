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
            material_name,
            actual_qty,
            `min`,
            `max`,
            `safety_stock`
        FROM `tabMaterial Stock` AS ms
        WHERE actual_qty <= `min`
    """, as_dict=True)