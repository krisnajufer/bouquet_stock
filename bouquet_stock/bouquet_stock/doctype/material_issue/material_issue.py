# Copyright (c) 2026, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from bouquet_stock.bouquet_stock.doctype.stock_ledger_entry.stock_ledger_entry import (
	make_sle,
	cancel_sle
)

class MaterialIssue(Document):
	def on_submit(self):
		make_sle(self, self)

	def on_cancel(self):
		cancel_sle(self, self)