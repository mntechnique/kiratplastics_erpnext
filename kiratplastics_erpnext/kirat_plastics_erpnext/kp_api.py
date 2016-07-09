# Copyright (c) 2015, MN Technique and Contributors.
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import money_in_words
from erpnext.stock.get_item_details import get_item_details, get_item_code
from erpnext.controllers.queries import get_filters_cond
from frappe.desk.reportview import get_match_cond
from frappe.utils import nowdate

def kp_sinv_item_query(doctype, txt, searchfield, start, page_len, filters=None):
	kp_filters = filters
	filters = {}

	conditions = []

	x = None

	try:
		x = frappe.db.sql("""select tabItem.name,tabItem.item_group,
			if(length(tabItem.item_name) > 40,
				concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
			if(length(tabItem.description) > 40, \
				concat(substr(tabItem.description, 1, 40), "..."), description) as decription
			from tabItem INNER JOIN `tabItem Customer Detail` AS B ON tabItem.name = B.parent
			where 
				tabItem.excise_chapter = '{exc}' AND B.customer_name = '{cn}' 
				and	tabItem.docstatus < 2
				and tabItem.has_variants=0
				and tabItem.disabled=0
				and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
				and (tabItem.`{key}` LIKE %(txt)s
					or tabItem.item_group LIKE %(txt)s
					or tabItem.item_name LIKE %(txt)s
					or tabItem.description LIKE %(txt)s)
				{fcond} {mcond}
			order by
				if(locate(%(_txt)s, tabItem.name), locate(%(_txt)s, tabItem.name), 99999),
				if(locate(%(_txt)s, tabItem.item_name), locate(%(_txt)s, tabItem.item_name), 99999),
				tabItem.idx desc,
				tabItem.name, tabItem.item_name
			limit %(start)s, %(page_len)s """.format(key=searchfield,
				fcond=get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
				mcond=get_match_cond(doctype).replace('%', '%%'), 
				exc=kp_filters.get("excise_chapter"), cn=kp_filters.get("cust_name")), {
					"today": nowdate(),
					"txt": "%%%s%%" % txt,
					"_txt": txt.replace("%", ""),
					"start": start,
					"page_len": page_len
				})
	except Exception, e:
		frappe.msgprint(e)
	else:
		return x

#Retrieve item details.
@frappe.whitelist() #overridden in hooks.py
def kp_get_item_details(args):
	#frappe.msgprint(args)
	result = get_item_details(args)

	item_code = result.get("item_code")
	
	chapter_head = frappe.db.get_value("Item", {"item_code": item_code}, "excise_chapter")

	#Item must have a chapter head. If not specified, return.
	if chapter_head == "": 
		frappe.msgprint(_("Excise Chapter Head not specified for item '%s'!" % (item_code)))
	
	result["kirat_excise_duty_rate"] = frappe.db.get_value("Item", item_code, "excise_duty_rate")

	#160709: Kirat Excise Price now pulled from Item Price doctype. 
	#Item Price records for Zero price list will not have any excise price.
	#Also, ZPL will override the customer's price list when invoice type is Sample or Challan.
	#Therefore, case of ZPL, excise price will have to be fetched from the customer's default price list if it exists or standard selling.
	
	#Convert args to dict.
	args_json = json.loads(args)
	price_list_for_pulling_excise_price = args_json["price_list"] #Longname!

	#If Zero Price List, lookup customer's default price list. If not found, use Standard Selling.
	if (args_json["price_list"].find("Zero") != -1):
		#frappe.msgprint("Zero Rate price list found. Attempting to find default price list to pull excise price from.")
		price_list_for_pulling_excise_price = frappe.db.get_value("Customer", args_json["customer"], "default_price_list")
		if (not price_list_for_pulling_excise_price) or (price_list_for_pulling_excise_price == ""):
			#frappe.msgprint("Default price list not found. Pulling excise price from Standard Selling")
			price_list_for_pulling_excise_price = "Standard Selling"

	kep = frappe.db.get_value("Item Price", {"price_list": price_list_for_pulling_excise_price, "item_code": item_code}, "kirat_excise_price")

	if not kep:
		frappe.throw(_("Item '%s' does not have a valid excise price." % (item_code)))

	result["kirat_excise_price"] = kep
	#result["kirat_excise_price"] = frappe.db.get_value("Item", item_code, "excise_price")


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
def kp_si_validate(self, method):
	self.kirat_total_excise_payable_in_words = money_in_words(self.kirat_excise_payable_total)

	#Check for duplicate items and items with zero rate for invoices other than type Sample/Challan.
	validate_repeating_items(self)
	validate_zero_amount_items(self)

def validate_repeating_items(self):
	"""Error when Same Company is entered multiple times in accounts"""
	item_list = []
	for itm in self.items:
		item_list.append(itm.item_code)

	if len(item_list)!= len(set(item_list)):
		frappe.throw(_("Some items have been selected more than once."))

def validate_zero_amount_items(self):
	zero_rate_items = []
	if (self.kirat_invoice_type != "Invoice for Sample") and (self.kirat_invoice_type != "Challan"):
		for itm in self.items:
			if itm.rate == 0.0:
				zero_rate_items.append(itm.item_code)

		if len(zero_rate_items) > 0:
			frappe.throw(_("Items with zero rate cannot be added to invoices that are not Invoices for Sample or Challans"))

def validate_zero_excise_price_items(self):
	zero_ep_items = []
	for itm in self.items:
		if not itm.kirat_excise_price or itm.kirat_excise_price == 0.0:
			zero_ep_items.append(itm.item_code)
	
	if len(zero_ep_items) > 0:
		frappe.throw(_("Items must have valid excise price.")) 