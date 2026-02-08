// Copyright (c) 2025, Jufer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
	refresh(frm) {
        frm.ignore_doctypes_on_cancel_all = ["Purchase Receipt"];
        showBtnCreatePrec(frm);
        filterMaterials(frm);
	},
    posting_date(frm){
        calculateMinMax(frm)
    }
});

frappe.ui.form.on("Purchase Order Item", {
    material(frm){
        calculateMinMax(frm)
    },
	qty(frm, cdt, cdn){
        calculateAmount(frm, cdt, cdn)
        checkMinMax(frm, cdt, cdn)
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

function showBtnCreatePrec(frm) {
    if (frm.doc.docstatus != 1 || frm.doc.status == "Diterima Sepenuhnya") {
        return
    }
    frm.add_custom_button("Purchase Receipt", () => {
        makePurchaseReceipt(frm)
    }, "Create")
}

function makePurchaseReceipt(frm) {
    frappe.model.open_mapped_doc({
        method: "bouquet_stock.bouquet_stock.doctype.purchase_order.purchase_order.make_purchase_receipt",
        frm: frm,
    }); 
}

function calculateMinMax(frm) {
    if (!frm.doc.posting_date) {
        frappe.msgprint(__('Tanggal Posting wajib diisi terlebih dahulu.'));
        return;
    }

    if (!frm.doc.materials || frm.doc.materials.length === 0) {
        frappe.msgprint(__('Tabel Material harus memiliki minimal satu baris data.'));
        return;
    }

    const has_empty_material = frm.doc.materials.some(row => !row.material);

    if (has_empty_material) {
        return;
    }

    frm.call('calculate_method')
        .then(r => {
            if (r.message) {
                let linked_doc = r.message;
                // lakukan proses lanjutan di sini
            }
        });
}


function checkMinMax(frm, cdt, cdn) {
    const curRow = locals[cdt][cdn];
    const min_max = frm.doc.min_max;

    for (const row of min_max) {
        if (curRow.material != row.material) {
            continue
        }

        if (row.max == 0) {
            return
        }
        
        if (curRow.qty > (row.max - row.current_qty)) {
            frappe.model.set_value(cdt, cdn, "qty", (row.max - row.current_qty));
        }
    }

    frm.refresh_field("materials");
}

function filterMaterials(frm) {
    frm.set_query("material", "materials", (doc) => {
        return {
            query:"bouquet_stock.bouquet_stock.doctype.purchase_order.purchase_order.filter_materials"
        }
    })
}