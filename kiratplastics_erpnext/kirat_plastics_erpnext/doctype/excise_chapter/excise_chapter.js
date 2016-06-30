// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('Excise Chapter', {
	refresh: function(frm) {
		if(!frm.doc.__islocal){	
			frm.add_custom_button(__('Update Items'), function(){
				if(frm.doc.__unsaved){
					msgprint("Please Save First");
					return;
				}
				frappe.call({
					method: "kiratplastics_erpnext.kirat_plastics_erpnext.doctype.excise_chapter.excise_chapter.update_items",
					args: {
						"excise_chapter": frm.doc.chapter_head,
						"rate_of_duty": frm.doc.rate_of_duty
					},
					freeze: true,
					freeze_message: __("Updating Excise Duty Rate Items"),
					callback: function(r){
						// if(!r.exc) {
						// 	frappe.msgprint(__("Items Updated Successfully"));
						// } else {
						// 	frappe.msgprint(__("Items could <br /> " + r.exc));
						// }
					}
				});
			});
		}
	}
});
