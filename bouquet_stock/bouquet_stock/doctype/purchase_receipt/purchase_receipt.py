# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bouquet_stock.bouquet_stock.doctype.stock_ledger_entry.stock_ledger_entry import (
	make_sle,
	cancel_sle
)

class PurchaseReceipt(Document):
	def on_submit(self):
		self.process_stock_ledger_entries()

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