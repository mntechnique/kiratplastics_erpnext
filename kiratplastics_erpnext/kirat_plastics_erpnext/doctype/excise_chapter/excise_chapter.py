# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

class ExciseChapter(NestedSet):
	nsm_parent_field = 'parent_excise_chapter'


@frappe.whitelist()
def update_items(excise_chapter, rate_of_duty):
	items_to_update = frappe.get_all("Item", fields=["item_code"], filters={"excise_chapter": excise_chapter})
	for item in items_to_update:
		upd_itm = frappe.get_doc("Item", item.item_code)
		upd_itm.excise_duty_rate = rate_of_duty
		upd_itm.save()
	frappe.db.commit()

