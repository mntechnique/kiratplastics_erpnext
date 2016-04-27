# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.utils import flt, cint, add_days, cstr
import json
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item, set_transaction_type
from erpnext.setup.utils import get_exchange_rate
from frappe.model.meta import get_field_precision
from erpnext.stock.get_item_details import get_item_details


def kp_sinv_item_query(doctype, txt, searchfield, start, page_len, filters):
	frappe.msgprint("kp_sinv_item_query called")
	return frappe.db.sql("""select item_code, item_name from `tabItem`
		where item_name = 'S12040-012A0Y-PLATE BACK'
		order by item_name DESC
		limit %(start)s, %(page_len)s""".format(**{
	}), {		
		'start': start,
		'page_len': page_len
	})

@frappe.whitelist()
def kp_get_item_details(args):
	#frappe.msgprint("Entered kp_get_item_details")
	result = get_item_details(args)

	#Extract itemname, load doctype, check if Excise chapter is set
	item_code = result.get("item_code")
	
	chapter_head = frappe.db.get_value("Item", {"item_code": item_code}, "excise_chapter")

	#Item must have a chapter head. If not specified, return.
	if chapter_head == "": 
		frappe.msgprint("Excise Chapter Head not specified for item '%s'!" % (item_code))
		return
	
	result["kirat_excise_duty_rate"] = frappe.db.get_value("Item", item_code, "excise_duty_rate")
	result["kirat_excise_price"] = frappe.db.get_value("Item", item_code, "excise_price")

	#Calculate final amount.

	
	item_rate = 0.0 #This will be set either to result[price_list_rate] or result[rate] depending on which is non-zero.
	item_rate_for_excise_calc = 0.0
	
	#Set item_rate
	if result["price_list_rate"] != 0.0:
		item_rate = result["price_list_rate"]
	else:
		item_rate = result["rate"]

	#Set item_rate_for_excise_calc
	if result["kirat_excise_price"] != 0.0:
		item_rate_for_excise_calc = result["kirat_excise_price"]
	else:
		item_rate_for_excise_calc = item_rate

	excise_duty_amt = kp_calculate_excise_duty_amt(result["qty"], item_rate_for_excise_calc, result["kirat_excise_duty_rate"])

	result["kirat_excise_duty_amt"] = excise_duty_amt

	assessable_value = result["qty"] * item_rate

	final_amt = assessable_value + excise_duty_amt

	result["amount"] = final_amt #Amount is overwritten later from taxes_and_totals.js
	
	return result

@frappe.whitelist()
def kp_calculate_excise_duty_amt(qty, price, rate):
	return (qty * price) * (rate / 100)
