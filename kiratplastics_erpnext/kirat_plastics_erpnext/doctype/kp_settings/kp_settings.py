# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class KPSettings(Document):
	def validate(self):
		self.validate_accounts()
		self.validate_repeating_companies()
	
	def validate_repeating_companies(self):
		ep_accounts_companies = []
		for entry in self.ep_accounts:
			ep_accounts_companies.append(entry.company)

		if len(ep_accounts_companies)!= len(set(ep_accounts_companies)):
			frappe.throw(_("Same Company is entered more than once in Default Excise Payable Account"))

	def validate_accounts(self):
		for entry in self.ep_accounts:
			"""Error when Company of Ledger account doesn't match with Company Selected"""
			if frappe.db.get_value("Account", entry.account, "company") != entry.company:
				frappe.throw(_("Account does not match with Company for Default Excise Payable Account"))

@frappe.whitelist()
def get_kp_settings(company):
	"""Return KP Settings for Company -
	income_account, receivable_account, payable_account, tax_account and cost_center"""

	out = {
		"ep_account" : frappe.db.get_value("KP Settings Excise Payable", {"company": company}, "account"),
		"zero_price_list" : frappe.db.get_single_value("Price List", "zero_price_list"),
	}

	if not out["ep_account"]:
		frappe.throw(_("Set Default Excise Payable Account in KP Settings"))

	return out

@frappe.whitelist()
def get_ep_account(company):
	ep_account = frappe.db.get_value("KP Settings Excise Payable", {"company": company}, "account")

	if not ep_account:
		frappe.throw(_("Set default Excise Payable account in KP Settings!"))

	return ep_account

@frappe.whitelist()
def get_zero_price_list():
	zpl = frappe.db.get_single_value("KP Settings", "zero_price_list")

	if not zpl:
		frappe.throw(_("Set Zero Price List in KP Settings!"))

	return zpl