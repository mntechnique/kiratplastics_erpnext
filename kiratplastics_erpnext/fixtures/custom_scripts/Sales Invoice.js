

frappe.ui.form.on("Sales Invoice Item", "rate", function(frm, cdt, cdn) {
   var sii = locals[cdt][cdn];
   if ((frm.doc.kirat_invoice_type != "Invoice for Sample") && (frm.doc.kirat_invoice_type != "Challan")) {
      if (sii.rate == 0.0) {
        msgprint("Rate cannot be zero for invoices other than Sample and Challan.");
      }
   }
});

frappe.ui.form.on("Sales Invoice Item", "kirat_excise_price", function(frm, cdt, cdn) {   
  cur_frm.cscript.calculate_item_values();
  refresh_field("items"); //This updates excise duty amount in the dialog when the excise rate is changed.
});

//Toggle readonly for Customer and Chapter Head depending on whether items exist.
frappe.ui.form.on("Sales Invoice Item", "items_add", function(frm, cdt, cdn) {
   set_customer_readonly(frm);
   set_chapter_head_readonly(frm);
   set_invoice_type_and_series_readonly(frm);
   set_excise_price_readonly(frm);
});

frappe.ui.form.on("Sales Invoice Item", "items_remove", function(frm) {
   set_customer_readonly(frm);
   set_chapter_head_readonly(frm);
   set_invoice_type_and_series_readonly(frm);
});
frappe.ui.form.on("Sales Invoice", "refresh", function(frm) {   
   set_excise_chapter_filter(frm);
   make_taxes_unsortable(frm);
   //set_invoice_type_and_series_readonly(frm);
   //set_chapter_head_readonly(frm);
   //set_customer_readonly(frm);
   set_item_filter_query(frm);
});

frappe.ui.form.on("Sales Invoice", "onload", function(frm) {
   make_taxes_unsortable(frm);
   get_company_account(frm); //Load excise account from settings and keep in global var for 1.
   get_zero_price_list(frm); //Load zero price list name from settings for 2
   set_excise_price_readonly(frm);
});

// Add Excise Row to Taxes and Charges
frappe.ui.form.on("Sales Invoice", "validate", function(frm) {
   inject_excise_row_and_append_taxes(frm);
});

frappe.ui.form.on("Sales Invoice", "kirat_invoice_type", function(frm) {
  set_naming_series_and_price_list(frm);
});

frappe.ui.form.on("Sales Invoice", "kirat_excise_chapter_head", function(frm) {
  frappe.model.with_doc("Excise Chapter", frm.doc.kirat_excise_chapter_head, function() { 
     var ec = frappe.model.get_doc("Excise Chapter", frm.doc.kirat_excise_chapter_head);
      frm.set_value("kirat_excise_chapter_name", ec.excise_chapter_name);
      frm.set_value("kirat_excise_chapter_rate", ec.rate_of_duty);
  });
});

frappe.ui.form.on("Sales Invoice", "customer", function(frm) {
  frappe.model.with_doc("Customer", frm.doc.customer, function() { 
     var cu = frappe.model.get_doc("Customer", frm.doc.customer);
      frm.set_value("kirat_cust_ecc_no", cu.kirat_ecc_no);
      frm.set_value("kirat_cust_cst_lst_no", cu.kirat_cst_lst_no);
      frm.set_value("kirat_cust_cst_lst_date", cu.kirat_cst_lst_date);
  });
});

cur_frm.cscript.customer = function() {
  var me = this;
  if(this.frm.updating_party_details) return;

  erpnext.utils.get_party_details(this.frm,
    "erpnext.accounts.party.get_party_details", {
      posting_date: this.frm.doc.posting_date,
      party: this.frm.doc.customer,
      party_type: "Customer",
      account: this.frm.doc.debit_to,
      price_list: this.frm.doc.selling_price_list,
    }, function() {
    me.apply_pricing_rule();
    set_naming_series_and_price_list(cur_frm);
  })
}

//Replaces calculation of item value
cur_frm.cscript.calculate_item_values = function() {    
    var me = this;
    if (!this.discount_amount_applied) {
        $.each(this.frm.doc["items"] || [], function(i, item) {
            frappe.model.round_floats_in(item);
            item.net_rate = item.rate;
            item.amount = flt(item.rate * item.qty, precision("amount", item));
            item.net_amount = item.amount;
            item.item_tax_amount = 0.0;
            calculate_excise_duty_amount(item);
            me.set_in_company_currency(item, ["price_list_rate", "rate", "amount", "net_rate", "net_amount"]);
        });
    }
}

//Prevent duplicate items. 
//Description property isnt added to the json until after the row gets added to the items list
//OR the line-item form is closed.
frappe.ui.form.on("Sales Invoice Item", "item_code", function(frm, cdt, cdn) {
   var sii = locals[cdt][cdn];
   for (var i = 0; i < frm.doc.items.length; i++) {
      if ((frm.doc.items[i].item_code == sii.item_code)) {
         if (frm.doc.items[i].hasOwnProperty("description")) {
           msgprint("Item " + sii.item_code + " has already been added!");
           sii.item_code = "";
           break;
         }
      }
   }
});
