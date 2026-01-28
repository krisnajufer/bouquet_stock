# Copyright (c) 2026, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Order
from frappe.query_builder.functions import Sum, Coalesce

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{
			"fieldtype": "Link",
			"fieldname": "material_code",
			"label": "ID",
			"width": 200,
			"options": "Material"
		},
		{
			"fieldtype": "Data",
			"fieldname": "material_name",
			"label": "Nama Material",
			"width": 200
		},
		{
			"fieldtype": "Int",
			"fieldname": "actual_qty",
			"label": "Qty Saat Ini",
			"width": 200,
			"default": 0
		},
		{
			"fieldtype": "Int",
			"fieldname": "safety_stock",
			"label": "Safety Stock",
			"width": 200,
			"default": 0
		},
		{
			"fieldtype": "Int",
			"fieldname": "min",
			"label": "Min",
			"width": 200,
			"default": 0
		},
		{
			"fieldtype": "Int",
			"fieldname": "max",
			"label": "Max",
			"width": 200,
			"default": 0
		},
	]

	return columns

def get_data(filters):
	
	MS = frappe.qb.DocType("Material Stock")
	Material = frappe.qb.DocType("Material")

	query = (
		frappe.qb.from_(Material)
		.select(
			Material.name.as_("material_code"), Material.material_name, MS.actual_qty, MS.safety_stock, MS.min, MS.max
		)
		.left_join(MS)
		.on(MS.material == Material.name)
	)

	if filters and filters.get("material_name"):
		material_name = filters.get("material_name")
		query = (
			query.where(
				Material.material_name.like(f"%{material_name}%")
			)
		)

	query = (
		query.groupby(Material.name)
	)


	return query.run(as_dict=True)