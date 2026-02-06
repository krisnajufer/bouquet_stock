# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from bouquet_stock.bouquet_stock.doctype.stock_ledger_entry.stock_ledger_entry import (
	make_sle,
	cancel_sle
)

class PurchaseReceipt(Document):
	def on_submit(self):
		self.process_stock_ledger_entries()
		self.update_purchase_order_items()

	def on_cancel(self):
		self.process_stock_ledger_entries(cancelled=True)

	def on_trash(self):
		frappe.db.delete("Stock Ledger Entry", {"document_name": self.name})

	def process_stock_ledger_entries(self, cancelled=False):
		for child in self.materials:
			if cancelled:
				cancel_sle(self, child)
			else:
				make_sle(self, child)

	def update_purchase_order_items(self):
		po_map = {}

		# 1. Group PR items by PO + PO Item
		for row in self.materials:
			if not row.purchase_order or not row.po_item:
				continue

			key = (row.purchase_order, row.po_item)
			po_map.setdefault(key, 0)
			po_map[key] += flt(row.qty)

		# 2. Update PO Item
		for (po, po_item), received_qty in po_map.items():
			self.update_po_item(po, po_item, received_qty)

		# 3. Update PO status
		self.update_po_status(set(k[0] for k in po_map.keys()))

	def update_po_item(self, purchase_order, po_item, received_qty):
		po_item_doc = frappe.get_doc("Purchase Order Item", po_item)

		total_received = flt(po_item_doc.received_qty) + received_qty
		percentage = (total_received / flt(po_item_doc.qty)) * 100 if po_item_doc.qty else 0

		po_item_doc.db_set({
			"received_qty": total_received,
			"received_percentage": percentage
		}, update_modified=False)

	def update_po_status(self, purchase_orders):
		for po in purchase_orders:
			items = frappe.get_all(
				"Purchase Order Item",
				filters={"parent": po},
				fields=["qty", "received_qty"]
			)

			if all(flt(i.received_qty) >= flt(i.qty) for i in items):
				status = "Diterima Sepenuhnya"
			elif any(flt(i.received_qty) > 0 for i in items):
				status = "Diterima Sebagian"
			else:
				status = "Dipesan"

			frappe.db.set_value("Purchase Order", po, "status", status)

