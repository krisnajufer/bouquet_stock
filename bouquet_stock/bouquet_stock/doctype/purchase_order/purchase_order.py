# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import(
	nowtime
)

class PurchaseOrder(Document):
	def on_submit(self):
		self.db_set("status", "Dipesan")

	def on_cancel(self):
		self.db_set("status", None)

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