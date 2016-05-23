# Copyright (c) 2015, MN Technique and Contributors.
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import money_in_words
from erpnext.stock.get_item_details import get_item_details, get_item_code

#Query for filtering items.
def kp_sinv_item_query(doctype, txt, searchfield, start, page_len, filters):

	return frappe.db.sql("""SELECT B.name, A.ref_code, B.item_group, B.item_name, B.description as description
	FROM `tabItem Customer Detail` AS A
	INNER JOIN `tabItem` AS B ON A.parent = B.name
	WHERE A.customer_name = '%s' AND B.excise_chapter = '%s';""" % (filters.get("cust_name"), filters.get("excise_chapter")))

#Retrieve item details.
@frappe.whitelist() #overridden in hooks.py
def kp_get_item_details(args):

	result = get_item_details(args)

	item_code = result.get("item_code")
	
	chapter_head = frappe.db.get_value("Item", {"item_code": item_code}, "excise_chapter")

	#Item must have a chapter head. If not specified, return.
	if chapter_head == "": 
		frappe.msgprint(_("Excise Chapter Head not specified for item '%s'!" % (item_code)))
	
	result["kirat_excise_duty_rate"] = frappe.db.get_value("Item", item_code, "excise_duty_rate")
	result["kirat_excise_price"] = frappe.db.get_value("Item", item_code, "excise_price")

	#Calculate final amount.
	item_rate = 0.0 #Set either to result[price_list_rate] or result[rate] depending on which is non-zero.
	item_rate_for_excise_calc = 0.0
	
	#Set item_rate
	if result["price_list_rate"] != 0.0:
		item_rate = result["price_list_rate"]
	else:
		item_rate = result["rate"]

	#Set item_rate_for_excise_calc
	#Deprecated: 160521: Excise Price will be entered for each item and excise calculation will use ONLY excise price.
	# if result["kirat_excise_price"] != 0.0:
	# 	item_rate_for_excise_calc = result["kirat_excise_price"]
	# else:
	# 	item_rate_for_excise_calc = item_rate
	item_rate_for_excise_calc = result["kirat_excise_price"]

	excise_duty_amt = kp_calculate_excise_duty_amt(result["qty"], item_rate_for_excise_calc, result["kirat_excise_duty_rate"])

	result["kirat_excise_duty_amt"] = excise_duty_amt
	result["kirat_total_amt_with_excise"] = excise_duty_amt + result["amount"]

	#result["customer_item_code"] = 
	
	return result

@frappe.whitelist()
def kp_calculate_excise_duty_amt(qty, price, rate):
	return (qty * price) * (rate / 100)

@frappe.whitelist()
def kp_validate(self, method):
	self.kirat_total_excise_payable_in_words = money_in_words(self.kirat_excise_payable_total)

	#Check for duplicate items and items with zero rate for invoices other than type Sample/Challan.
	if self.items.length != set(self.items).length:
		frappe.throw(_("Some items have been selected twice."))