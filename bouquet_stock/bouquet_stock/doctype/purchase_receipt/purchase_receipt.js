// Copyright (c) 2025, Jufer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
        frm.ignore_doctypes_on_cancel_all = ["Purchase Order"];
	},
});
