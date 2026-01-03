# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockLedgerEntry(Document):
	pass

def make_sle(parent, child):
	last_qty_change = calculate_past_sle(child.material, parent.posting_date, parent.posting_time, parent.modified)
	qty = child.qty if parent.doctype in ("Purchase Receipt") else child.qty * -1
	sle = frappe.new_doc("Stock Ledger Entry")
	sle.document_type = parent.doctype
	sle.document_name = parent.name
	sle.material = child.material
	sle.posting_date = parent.posting_date
	sle.posting_time = parent.posting_time
	sle.qty_change = qty
	sle.qty_after_transaction = last_qty_change + qty
	sle.save()
	update_material_stock(child.material)

def calculate_past_sle(material, posting_date, posting_time, modified):
	filters = {
		"material": material,
		"timestamp": f"{posting_date} {posting_time}",
		"modified": modified
	}
	query = """
		SELECT SUM(qty_change) AS last_qty_change
		FROM `tabStock Ledger Entry`
		WHERE material = %(material)s AND TIMESTAMP(posting_date, posting_time) <= %(timestamp)s AND modified < %(modified)s  AND is_cancelled = 0 
	"""
	
	result = frappe.db.sql(query, filters, as_dict=True)
	
	return result[0].last_qty_change if result and result[0].last_qty_change else 0

def cancel_sle(parent, child):
	filters = {
		"document_type" : parent.doctype,
		"document_name" : parent.name,
		"material": child.material
	}
	
	frappe.db.set_value("Stock Ledger Entry", filters, "is_cancelled", 1)
	current_sle = frappe.db.get_value("Stock Ledger Entry", filters, "*")

	repost_future_sle(child.material, parent.posting_date, parent.posting_time, current_sle)
	update_material_stock(child.material)
	
def repost_future_sle(material, posting_date, posting_time, current_sle):
	last_qty_change = calculate_past_sle(material, posting_date, posting_time, current_sle.creation)
	qty_after_transaction = 0
	data = get_future_sle(material, posting_date, posting_time, current_sle.creation)

	for row in data:
		qty_after_transaction += last_qty_change + row.qty_change

		frappe.db.set_value("Stock Ledger Entry", row.name, "qty_after_transaction", qty_after_transaction)
	

def get_future_sle(material, posting_date, posting_time, creation):
	filters = {
		"material": material,
		"timestamp": f"{posting_date} {posting_time}",
		"creation": creation
	}
	query = """
		SELECT name, qty_change
		FROM `tabStock Ledger Entry`
		WHERE material = %(material)s AND TIMESTAMP(posting_date, posting_time) >= %(timestamp)s AND creation > %(creation)s  AND is_cancelled = 0
	"""
	result = frappe.db.sql(query, filters, as_dict=True, debug=True)
	
	return result

def update_material_stock(material):
	stock = frappe.db.get_value(
		"Material Stock",
		{"material": material},
		"name"
	)

	if not stock:
		return

	qty = calculate_material_stock(material)

	frappe.db.set_value(
		"Material Stock",
		stock,
		{
			"actual_qty": qty["actual_qty"],
			"in_qty": qty["in_qty"]
		}
	)



def calculate_material_stock(material):
	result = frappe.db.sql(
		"""
		SELECT
			COALESCE(SUM(qty_change), 0) AS actual_qty,
			COALESCE(SUM(
				CASE 
					WHEN document_type = 'Purchase Receipt' 
					THEN qty_change 
					ELSE 0 
				END
			), 0) AS in_qty
		FROM `tabStock Ledger Entry`
		WHERE material = %(material)s AND is_cancelled = 0
		""",
		{"material": material},
		as_dict=True
	)[0]

	return result
