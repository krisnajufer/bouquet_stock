(()=>{(function(){if(window.__stock_alert_loaded)return;window.__stock_alert_loaded=!0;let o=!1;function i(){o||frappe.call({method:"bouquet_stock.bouquet_stock.doctype.material_stock.material_stock.get_critical_stock",callback(a){a.message&&a.message.length&&r(a.message)}})}function r(a){o=!0;let l=a.map(t=>`
            <tr>
                <td>${t.material}</td>
                <td>${t.material_name}</td>
                <td>${t.actual_qty}</td>
                <td>${t.safety_stock}</td>
                <td>${t.min}</td>
                <td>${t.max}</td>
                <td>
                    <button 
                        class="btn btn-sm btn-primary order-item"
                        data-item="${t.material}"
                        data-name="${t.material_name}"
                        data-qty="${t.max-t.actual_qty||1}">
                        Pesan
                    </button>
                </td>
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
                                    <th>Nama Material</th>
                                    <th>Stok Aktual</th>
                                    <th>Safety Stock</th>
                                    <th>Min</th>
                                    <th>Max</th>
                                    <th>Aksi</th>
                                </tr>
                            </thead>
                            <tbody>${l}</tbody>
                        </table>
                    `}],size:"extra-large"});e.show(),e.$wrapper.find(".modal-header .close").remove(),e.$wrapper.on("click",".order-item",function(){let t=$(this).data("item"),n=$(this).data("qty"),s=$(this).data("name");frappe.route_options={materials:[{material:t,material_name:s,qty:n}]},e.hide(),frappe.new_doc("Purchase Order")})}frappe.after_ajax(()=>{console.log("OKE SUKSES - AFTER AJAX"),i()})})();})();
//# sourceMappingURL=global.bundle.2VN3I4JX.js.map
