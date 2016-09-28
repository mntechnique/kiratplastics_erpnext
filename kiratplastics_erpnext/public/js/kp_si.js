//Kirat Plastics Script

var excise_account;
var zero_price_list;

function get_company_account(frm) {
   frappe.call({
      method: "kiratplastics_erpnext.kirat_plastics_erpnext.doctype.kp_settings.kp_settings.get_ep_account",
      args: {
         "company": frm.doc.company
      },
      callback: function(r) {
         excise_account = r.message; //excise_account is a global variable.
      }
   });
}

function get_zero_price_list(frm) {
   frappe.call({
      method: "kiratplastics_erpnext.kirat_plastics_erpnext.doctype.kp_settings.kp_settings.get_zero_price_list",
      args: {},
      callback: function(r) {
        zero_price_list = r.message; //zero_price_list is a global variable
      }
   });
}

function set_excise_chapter_filter(frm) {
   //Set query filter
    frm.set_query("kirat_excise_chapter_head", function() {
        return {
            "filters": {
                "is_group": "No"
            }
        };
    });
}

function make_taxes_unsortable(frm) {
   frm.page.body.find('[data-fieldname="taxes"] [data-idx] .data-row').removeClass('sortable-handle');
}

function calculate_excise_duty_amount(item) {
   var item_price;
   var item_price_for_excise_calc;

   if (item.price_list_rate != 0) {
      item_price = item.price_list_rate;
   } else {
      item_price = item.rate;
   }
 
   item_price_for_excise_calc = item.kirat_excise_price;
   //Deprecated: 160521: Calculate excise rate ONLY with excise price.
   //It WILL be entered manually for each item.
   // if (item.kirat_excise_price != 0) {
   //    item_price_for_excise_calc = item.kirat_excise_price;
   // } else {
   //    item_price_for_excise_calc = item_price; //Price list rate or rate.
   // }
   
   var excise_duty_amt = (item.qty * item_price_for_excise_calc) * (item.kirat_excise_duty_rate / 100);
   item.kirat_excise_duty_amt = excise_duty_amt;
   item.kirat_total_amt_with_excise = item.amount + excise_duty_amt;
}

function inject_excise_row_and_append_taxes(frm) {
   
   //Calculate total excise amount for all items
    var items = frm.doc.items;
    var total_ed = 0.0;
    var total_ea = 0.0; //Total Amount with Excise.

    if (frm.doc.kirat_invoice_type == "Challan") {
      total_ed = 0.0;
      total_ea = 0.0;
    } else {
      if (items) {
        for (var i = 0; i < items.length; i++) {
           total_ed += items[i].kirat_excise_duty_amt;
           total_ea += items[i].kirat_total_amt_with_excise;
        }
      }
    } 

    //Set total fields in Doc
    frm.set_value("kirat_excise_payable_total", total_ed);
    frm.set_value("kirat_amount_with_excise_total", total_ea);

    var taxes_temp = frm.doc.taxes;
    
    //Find and delete Excise rows from taxes_temp;
    if (taxes_temp) {
      var taxes_temp_temp = taxes_temp; //!Removing elements from array while iterating over it may be hazardous.
      
      for(var i = 0; i <= taxes_temp_temp.length - 1; i++) {
        if (taxes_temp_temp[i].description.indexOf("Excise") > -1) {
          taxes_temp.splice(i, 1);
        }
      }
    }
        
    //Clear the taxes table.
    frm.clear_table("taxes");

    //Inject Excise row as first row.
    var si = locals['Sales Invoice'][si];
    var ed = frappe.model.add_child(frm.doc,'Sales Taxes and Charges','taxes');   
    //ed.account_head = "Excise Payable - KPPL";
    ed.account_head = excise_account; //1
    ed.charge_type = "Actual";
    ed.description = "Excise Duty Payable";
    ed.tax_amount = total_ed;
    
    if (!taxes_temp) { return; } //to prevent taxes_temp nullref in for loop.

    for (var i = 0; i < taxes_temp.length; i++) {
        var tr = frappe.model.add_child(frm.doc,'Sales Taxes and Charges','taxes');
        tr.account_head = taxes_temp[i].account_head;
        tr.description = taxes_temp[i].description;

        if (taxes_temp[i].charge_type != "Actual") {
           tr.charge_type = "On Previous Row Total";
           tr.row_id = 1;
           tr.rate = taxes_temp[i].rate;
        } else {
           tr.charge_type = taxes_temp[i].charge_type;
           tr.tax_amount = taxes_temp[i].tax_amount;
        }
    }
}

function set_item_filter_query(frm) {
   cur_frm.set_query("item_code", "items", function() {
      return {
        query: "kiratplastics_erpnext.kirat_plastics_erpnext.kp_api.kp_sinv_item_query",
        filters: {
           "cust_name": frm.doc.customer,
           "excise_chapter": frm.doc.kirat_excise_chapter_head
        }
      };
   });
}

function set_customer_readonly(frm) {
  if (frm.doc.items) {
    frm.set_df_property("customer", "read_only", (frm.doc.items.length > 0));
  }
}
function set_chapter_head_readonly(frm) {
  if (frm.doc.items) {
   frm.set_df_property("kirat_excise_chapter_head", "read_only", (frm.doc.items.length > 0));
  }
}
function set_invoice_type_and_series_readonly(frm) {
  if (frm.doc.items) {
   frm.set_df_property("kirat_invoice_type", "read_only", (frm.doc.items.length > 0));
   frm.set_df_property("naming_series", "read_only", (frm.doc.items.length > 0));
  }
}
function set_excise_price_readonly(frm) { 
    var df = frappe.meta.get_docfield("Sales Invoice Item","kirat_excise_price", cur_frm.doc.name);
    df.read_only = (frm.doc.kirat_invoice_type != "Supplementary Invoice");
}



function set_naming_series_and_price_list(frm) {
   switch (frm.doc.kirat_invoice_type) {
     case "Invoice for Sample":
        frm.set_value("update_stock", 1);
        frm.set_value("selling_price_list", zero_price_list); //2
        break;

     case "Challan":
        frm.set_value("update_stock", 1);
        frm.set_value("selling_price_list", zero_price_list); //2
        break;

     case "Export":
        frm.set_value("update_stock", 1);
        frm.set_value("naming_series", "KPX16-17/");
        if ((!frm.doc.selling_price_list) || (frm.doc.selling_price_list.indexOf('Zero') >= 0)) { 
          frm.set_value("selling_price_list", "Standard Selling"); 
        } //2
        break;
     case "Supplementary Invoice":
        frm.set_value("update_stock", 0);

        if ((!frm.doc.selling_price_list) || (frm.doc.selling_price_list.indexOf('Zero') >= 0)) { 
          frm.set_value("selling_price_list", "Standard Selling"); //2
        }
        break;
     default:
        frm.set_value("update_stock", 1);
        frm.set_value("naming_series", "KP16-17/");
        if ((!frm.doc.selling_price_list) || (frm.doc.selling_price_list.indexOf('Zero') >= 0)) { 
          frm.set_value("selling_price_list", "Standard Selling"); //2
        }
        break;
  }
}


// function set_naming_series_and_price_list(frm) {
//    frm.set_value("naming_series", "KP16-17/"); //Default naming series.

//    switch (frm.doc.kirat_invoice_type) {
//      case "Supplementary Invoice":
//         //frm.set_value("naming_series", "SINV-SUP-");
//         frm.set_value("selling_price_list", "Standard Selling");
//         break;
//      case "Invoice for Sample":
//         //frm.set_value("naming_series", "SINV-SMP-");
//         frm.set_value("selling_price_list", zero_price_list); //2
//         break;
//      case "Challan":
//         //frm.set_value("naming_series", "SINV-CHL-");
//         frm.set_value("selling_price_list", zero_price_list); //2
//         break;
//      case "Export":
//         frm.set_value("naming_series", "KPX16-17/");
//         frm.set_value("selling_price_list", "Standard Selling"); //2
//         break;
//      default:
//         //frm.set_value("naming_series", "SINV-");
//         frm.set_value("selling_price_list", "Standard Selling");
//         frm.set_value("naming_series", "KP16-17/"); //Additional safeguard.
//         break;
//   }
// }
