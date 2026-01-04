(()=>{(function(){if(window.__stock_alert_loaded)return;window.__stock_alert_loaded=!0;let o=!1;function i(){o||frappe.call({method:"bouquet_stock.bouquet_stock.doctype.material_stock.material_stock.get_critical_stock",callback(t){t.message&&t.message.length&&l(t.message)}})}function l(t){o=!0;let r=t.map(a=>`
            <tr>
                <td>${a.material}</td>
                <td>${a.actual_qty}</td>
                <td>${a.min}</td>
            </tr>
        `).join(""),e=new frappe.ui.Dialog({title:__("Peringatan Stok Kritis"),static:!0,fields:[{fieldtype:"HTML",options:`
                        <p style="color:red; font-weight:bold">
                            Terdapat material dengan stok di bawah batas minimum.
                            Silakan lakukan pemesanan segera.
                        </p>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Material</th>
                                    <th>Stok Aktual</th>
                                    <th>Stok Minimum</th>
                                </tr>
                            </thead>
                            <tbody>${r}</tbody>
                        </table>
                    `}],primary_action_label:__("Pesan"),primary_action(){e.hide(),frappe.set_route("List","Purchase Order")}});e.show(),e.$wrapper.find(".modal-header .close").remove()}frappe.after_ajax(()=>{console.log("OKE SUKSES - AFTER AJAX"),i()})})();})();
//# sourceMappingURL=global.bundle.CK726MJ5.js.map
