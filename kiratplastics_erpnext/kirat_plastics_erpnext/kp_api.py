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
from frappe.model.naming import make_autoname
import frappe.permissions
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc



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


@frappe.whitelist(allow_guest=True)
def kp_calculate_item_values(self, method):	
	for item in self.get("items"):
		self.round_floats_in(item)

		if item.discount_percentage == 100:
			item.rate = 0.0
		elif not item.rate:
			item.rate = flt(item.price_list_rate *
				(1.0 - (item.discount_percentage / 100.0)), item.precision("rate"))
		
		item.net_rate = item.rate
		
		#no need to check whether item rate or price_list_rate at this point.
		#item.amount = flt(item.rate * item.qty,	item.precision("amount"))
		item_rate_for_excise_calc = 0.0
		if item.kirat_excise_price != 0.0:
			item_rate_for_excise_calc = item.kirat_excise_price
		else:
			item_rate_for_excise_calc = item.rate

		amt = flt(item.rate * item.qty,	item.precision("amount"))
		excise_duty_amt = kp_calculate_excise_duty_amt(item.qty, item_rate_for_excise_calc, item.kirat_excise_duty_rate)

		item.amount = amt + excise_duty_amt
		item.net_amount = item.amount

		self.run_method("set_in_company_currency", item, ["price_list_rate", "rate", "net_rate", "amount", "net_amount"])

		item.item_tax_amount = 0.0



	# for item in self.doc.get("items"):
	# 	self.doc.round_floats_in(item)

	# 	if item.discount_percentage == 100:
	# 		item.rate = 0.0
	# 	elif not item.rate:
	# 		item.rate = flt(item.price_list_rate *
	# 			(1.0 - (item.discount_percentage / 100.0)), item.precision("rate"))

	# 	item.net_rate = item.rate
	# 	item.amount = flt(item.rate * item.qty,	item.precision("amount"))
	# 	item.net_amount = item.amount

	# 	self.set_in_company_currency(item, ["price_list_rate", "rate", "net_rate", "amount", "net_amount"])

	# 	item.item_tax_amount = 0.0