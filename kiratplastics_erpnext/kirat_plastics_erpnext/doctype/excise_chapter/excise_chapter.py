# -*- coding: utf-8 -*-
# Copyright (c) 2015, MN Technique and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.nestedset import NestedSet

class ExciseChapter(NestedSet):
	nsm_parent_field = 'parent_excise_chapter'
