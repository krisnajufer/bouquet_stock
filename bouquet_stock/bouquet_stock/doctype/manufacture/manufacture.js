// Copyright (c) 2025, Jufer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Manufacture", {
	refresh(frm) {

	},
});

frappe.ui.form.on("Manufacture Bouquet Item", {
	refresh(frm) {

	},

    bouquet(frm, cdt, cdn){
        calculateMaterial(frm, cdt, cdn)
    },
    qty(frm, cdt, cdn){
        calculateMaterial(frm, cdt, cdn)
    }
});

async function calculateMaterial(frm, cdt, cdn) {
    const curRow = locals[cdt][cdn]
    if (curRow.qty > 0) {
        const result = await frappe.call({
            method: 'bouquet_stock.bouquet_stock.doctype.manufacture.manufacture.calculate_material_bouquet',
            args: {
                bouquet_name: curRow.bouquet,
                bouquet_qty: curRow.qty
            }
        })
        let status = "Bisa"
        frm.doc.materials = []
        for (const row of result.message) {
            if (row.status == "Tidak Cukup") {
                status = "Tidak Bisa"
            }
            frm.add_child("materials", row)
        }

        curRow.status = status;
        frm.refresh_field("bouquets");
        frm.refresh_field("materials");
    }
    
}
