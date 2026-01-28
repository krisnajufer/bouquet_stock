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
			"fieldname": "current_qty",
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
	
	SLE = frappe.qb.DocType("Stock Ledger Entry")
	Material = frappe.qb.DocType("Material")

	stock_query = (
		frappe.qb.from_(Material)
		.select(
			Material.name.as_("material_code"), Material.material_name, Sum(Coalesce(SLE.qty_change, 0)).as_("current_qty")
		)
		.left_join(SLE)
		.on(SLE.material == Material.name)
	)

	if filters and filters.get("material_name"):
		material_name = filters.get("material_name")
		stock_query = (
			stock_query.where(
				Material.material_name.like(f"%{material_name}%")
			)
		)

	stock_query = (
		stock_query.groupby(Material.name)
	)

	method_query = (
		frappe.qb.from_(Material)
		.select(
			Material.name, Coalesce(SLE.safety_stock, 0).as_("safety_stock"), Coalesce(SLE.min, 0).as_("min"), Coalesce(SLE.max, 0).as_("max")
		)
		.left_join(SLE)
		.on(SLE.material == Material.name)
	)

	if filters and filters.get("material_name"):
		material_name = filters.get("material_name")
		method_query = (
			method_query.where(
				Material.material_name.like(f"%{material_name}%")
			)
		)

	method_query = (
		method_query.groupby(Material.name)
		.orderby(SLE.posting_date, order=Order.desc)
		.orderby(SLE.posting_time, order=Order.desc)
		.orderby(SLE.creation, order=Order.desc)
		.limit(1)	
	)
	
	res_stock = stock_query.run(as_dict=True)
	res_method = method_query.run(as_dict=True)

	method_qty = {}

	for row in res_method:
		method_qty.update(
			{
				row.name : frappe._dict({
					"safety_stock": row.safety_stock,
					"min": row.min,
					"max": row.max,
				})
			})
		
	for idx, row in enumerate(res_stock):
		if row.get("material_code") not in method_qty:
			continue
		key = row.get("material_code") 
		res_stock[idx].update(method_qty.get(key))

	return res_stock