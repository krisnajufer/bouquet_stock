# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bouquet_stock.bouquet_stock.doctype.stock_ledger_entry.stock_ledger_entry import (
	make_sle,
	cancel_sle
)

class Manufacture(Document):
	def validate(self):
		self.validation_material_stock()
		
	def on_submit(self):
		self.process_bouquet_material()
	
	def on_cancel(self):
		self.process_bouquet_material(cancelled=True)

	def process_bouquet_material(self, cancelled=False):
		for b in self.bouquets:
			bouquet = frappe.get_doc("Bouquet", b.bouquet)
			for row in bouquet.bouquet_material:
				child = frappe._dict({
					"material": row.material,
					"qty": float(b.qty) * float(row.qty)
				})
				self.process_stock_ledger_entries(child, cancelled)
	
	def process_stock_ledger_entries(self, child, cancelled=False):
		if cancelled:
			cancel_sle(self, child)
		else:
			make_sle(self, child)
	
	def validation_material_stock(self, cancelled=False):
		for b in self.bouquets:
			bouquet = frappe.get_doc("Bouquet", b.bouquet)
			for row in bouquet.bouquet_material:
				actual_qty = frappe.db.get_value("Material Stock", {"material": row.material}, "actual_qty")
				child = frappe._dict({
					"material": row.material,
					"qty": float(b.qty) * float(row.qty)
				})
				if not cancelled and child.qty > actual_qty:
					frappe.throw(f"Stok Material <b>{row.material}</b> tidak mencukupi")
		
@frappe.whitelist()
def calculate_material_bouquet(bouquet_name, bouquet_qty):
	bouquet = frappe.get_doc("Bouquet", bouquet_name)

	material_needs = []
	for row in bouquet.bouquet_material:
		actual_qty = frappe.db.get_value("Material Stock", {"material": row.material}, "actual_qty")
		material_name = frappe.db.get_value("Material", row.material, "material_name")
		value = {
			"material": row.material,
			"material_name": material_name,
			"qty": float(row.qty) * float(bouquet_qty),
			"current_qty": actual_qty,
			"status": "Cukup"
		}
		if value["current_qty"] < value["qty"]:
			value["status"] = "Tidak Cukup"
		material_needs.append(value)

	return material_needs