# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Manufacture(Document):
	pass

@frappe.whitelist()
def calculate_material_bouquet(bouquet_name, bouquet_qty):
	bouquet = frappe.get_doc("Bouquet", bouquet_name)

	material_needs = []
	for row in bouquet.bouquet_material:
		actual_qty = frappe.db.get_value("Material Stock", {"material": row.material}, "actual_qty")
		value = {
			"material": row.material,
			"qty": float(row.qty) * float(bouquet_qty),
			"current_qty": actual_qty,
			"status": "Cukup"
		}
		if value["current_qty"] < value["qty"]:
			value["status"] = "Tidak Cukup"
		material_needs.append(value)

	return material_needs