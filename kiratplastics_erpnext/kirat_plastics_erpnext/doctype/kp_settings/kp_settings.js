// Copyright (c) 2016, MN Technique and contributors
// For license information, please see license.txt

frappe.ui.form.on('KP Settings', {
	refresh: function(frm) {
		cur_frm.set_query("zero_price_list", function() {
	        return {
	            "filters": {
	                "selling": 1
	            }
	        };
	    });
	    cur_frm.set_query("account", "ep_accounts", function() {
	        return {
	            "filters": {
	                "is_group": 0
	            }
	        };
	    });
	}
});
