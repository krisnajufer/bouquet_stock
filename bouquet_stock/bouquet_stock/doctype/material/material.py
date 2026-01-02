# Copyright (c) 2025, Jufer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Material(Document):

	def after_insert(self):
		make_material_stock(self.material_name)

	def on_trash(self):
		delete_material_stock(self.material_name)

def make_material_stock(material):
    material_stock = frappe.new_doc("Material Stock")
    material_stock.material = material
    material_stock.insert(ignore_permissions=True)
    
def delete_material_stock(material):
    frappe.db.delete("Material Stock", {"material": material})