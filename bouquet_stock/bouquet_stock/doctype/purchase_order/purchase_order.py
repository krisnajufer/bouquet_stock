# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import(
	nowtime
)

from bouquet_stock.bouquet_stock.doctype.material_stock.material_stock import get_critical_stock

class PurchaseOrder(Document):
	def validate(self):
		total = 0
		for row in self.materials:
			row.amount = row.qty * row.price

			total += row.amount
		self.grand_total = total

	def on_submit(self):
		self.db_set("status", "Dipesan")

	def on_cancel(self):
		self.db_set("status", None)

	def on_trash(self):
		frappe.db.delete("Stock Ledger Entry", {"document_name": self.name})

	@frappe.whitelist()
	def calculate_method(self):
		self.min_max = []
		for row in self.materials:
			result = self.get_min_max(row)
			self.append("min_max", {
				"safety_stock": result["safety_stock"],
				"min": result["min"],
				"max": result["max"],
				"current_qty": result["current_qty"],
				"lead_time": 2,
				"material": row.material
			})
			row.qty =  result["max"] - result["current_qty"] if result["max"] > 0 else row.qty

	def get_min_max(self, row):
		lead_time = 2

		res = frappe.db.sql("""
			SELECT
				MAX(ABS(qty_change)) AS max_qty,
				SUM(ABS(qty_change)) / %(interval_days)s AS avg_qty
			FROM `tabStock Ledger Entry`
			WHERE document_type = 'Manufacture'
			AND material = %(material)s
			AND is_cancelled = 0
			AND posting_date BETWEEN
				DATE_SUB(%(posting_date)s, INTERVAL %(interval_days)s DAY)
				AND %(posting_date)s
		""", {
			"posting_date": self.posting_date,
			"interval_days": 30,
			"material": row.material
		}, as_dict=True, debug=True)[0]

		max_qty = res.max_qty or 0
		avg_qty = res.avg_qty or 0

		safety_stock = max((max_qty - avg_qty) * lead_time, 0)
		min_qty = avg_qty * lead_time + safety_stock
		max_qty_stock = min_qty * 2
		actual_qty = frappe.db.get_value("Material Stock", {"material": row.material}, "actual_qty")
		return {
			"safety_stock": safety_stock,
			"min": min_qty,
			"max": max_qty_stock,
			"current_qty": actual_qty
		}


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	def set_missing_values(source, target):
		for row in target.materials:
			row.purchase_order = source.name
		target.update({"posting_time": nowtime()})

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Receipt",
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"po_item": "name"
				}
			},
		},
		target_doc,
		set_missing_values,
	)

	return doc


@frappe.whitelist()
def filter_materials(doctype, txt, searchfield, start, page_len, filters):
	critical_stocks = get_critical_stock()

	material_criticals = []

	for row in critical_stocks:
		material_criticals.append(row.material)

	if not material_criticals:
		return []

	Material = frappe.qb.DocType(doctype)
	txt =f"%{txt}%"
	query = (
		frappe.qb.from_(Material)
		.select(Material.name.as_("value"), Material.material_name.as_("text"))
		.where(
			(Material.name.isin(material_criticals))
		)
		.where(
			(Material.name.like(txt))
			| (Material.material_name.like(txt))
		)
	)

	result = query.run()

	return result