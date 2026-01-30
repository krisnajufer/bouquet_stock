(() => {
  // ../bouquet_stock/bouquet_stock/public/js/global.bundle.js
  (function() {
    if (window.__stock_alert_loaded)
      return;
    window.__stock_alert_loaded = true;
    let dialog_shown = false;
    function check_stock() {
      if (dialog_shown)
        return;
      frappe.call({
        method: "bouquet_stock.bouquet_stock.doctype.material_stock.material_stock.get_critical_stock",
        callback(r) {
          if (r.message && r.message.length) {
            show_dialog(r.message);
          }
        }
      });
    }
    function show_dialog(data) {
      dialog_shown = true;
      let rows = data.map((d) => `
            <tr>
                <td>${d.material}</td>
                <td>${d.material_name}</td>
                <td>${d.actual_qty}</td>
                <td>${d.safety_stock}</td>
                <td>${d.min}</td>
                <td>${d.max}</td>
                <td>
                    <button 
                        class="btn btn-sm btn-primary order-item"
                        data-item="${d.material}"
                        data-qty="${d.max - d.actual_qty || 1}">
                        Pesan
                    </button>
                </td>
            </tr>
        `).join("");
      const dialog = new frappe.ui.Dialog({
        title: __("Peringatan Stok Kritis"),
        static: true,
        fields: [
          {
            fieldtype: "HTML",
            options: `
                        <p style="color:red; font-weight:bold">
                            Terdapat material dengan stok di bawah batas minimum.
                            Silakan lakukan pemesanan segera.
                        </p>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Material</th>
                                    <th>Nama Material</th>
                                    <th>Stok Aktual</th>
                                    <th>Safety Stock</th>
                                    <th>Min</th>
                                    <th>Max</th>
                                    <th>Aksi</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    `
          }
        ],
        size: "extra-large"
      });
      dialog.show();
      dialog.$wrapper.find(".modal-header .close").remove();
      dialog.$wrapper.on("click", ".order-item", function() {
        const material = $(this).data("item");
        const qty = $(this).data("qty");
        frappe.route_options = {
          materials: [
            {
              material,
              qty
            }
          ]
        };
        dialog.hide();
        frappe.new_doc("Purchase Order");
      });
    }
    frappe.after_ajax(() => {
      console.log("OKE SUKSES - AFTER AJAX");
      check_stock();
    });
  })();
})();
//# sourceMappingURL=global.bundle.ZNYDTNQ5.js.map
