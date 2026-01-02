// Copyright (c) 2025, Jufer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
	refresh(frm) {

	},
});

frappe.ui.form.on("Purchase Order Item", {
    material(frm, cdt, cdn){

    },
	qty(frm, cdt, cdn){
        calculateAmount(frm, cdt, cdn)
    },
    price(frm, cdt, cdn){
        calculateAmount(frm, cdt, cdn)
    }
});


function calculateAmount(frm, cdt, cdn) {
    const curRow = locals[cdt][cdn]
    if (!curRow.qty || !curRow.price) {
        return
    }

    const amount = curRow.price * curRow.qty;

    frappe.model.set_value(cdt, cdn, "amount", amount);
    frm.refresh_field("materials");
    calculateGrandTotal(frm);
}

function calculateGrandTotal(frm){
    const materials = frm.doc.materials;
    if (!materials) {
        return
    }

    let grandTotal = 0;
    for (const row of materials) {
        grandTotal += row.amount;
    }

    frm.set_value("grand_total", grandTotal);
    frm.refresh_field("grand_total");
}