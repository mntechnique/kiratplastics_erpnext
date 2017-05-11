//cur_frm.add_fetch("excise_chapter", "rate_of_duty", "excise_duty_rate");

frappe.ui.form.on("Item", "excise_chapter", function(frm) {
   if (!cur_frm.doc.excise_chapter) {
      cur_frm.set_value("excise_duty_rate", null);
   } else {
      frappe.model.with_doc("Excise Chapter", cur_frm.doc.excise_chapter, function(frm){
         var ec = frappe.model.get_doc("Excise Chapter", cur_frm.doc.excise_chapter);
         cur_frm.set_value("excise_duty_rate", ec.rate_of_duty);
      });
   }
});

frappe.ui.form.on("Item", "refresh", function(frm) {
    frm.set_query("excise_chapter", function() {
        return {
            "filters": {
                "is_group": "No"
            }
        };
    });
});
