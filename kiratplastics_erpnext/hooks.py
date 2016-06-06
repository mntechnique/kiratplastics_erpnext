# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "kiratplastics_erpnext"
app_title = "Kirat Plastics ERPNext"
app_publisher = "MN Technique"
app_description = "ERPNext extensions for Kirat Plastics Pvt. Ltd."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@castlecraft.in"
app_version = "1.1.2"
app_license = "GPL v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/kiratplastics_erpnext/css/kiratplastics_erpnext.css"
app_include_js = "/assets/kiratplastics_erpnext/js/kp_si.js"

# include js, css files in header of web template
# web_include_css = "/assets/kiratplastics_erpnext/css/kiratplastics_erpnext.css"
# web_include_js = "/assets/kiratplastics_erpnext/js/kiratplastics_erpnext.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "kiratplastics_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "kiratplastics_erpnext.install.before_install"
# after_install = "kiratplastics_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kiratplastics_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"validate": "kiratplastics_erpnext.kirat_plastics_erpnext.kp_api.kp_si_validate",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"kiratplastics_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"kiratplastics_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"kiratplastics_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kiratplastics_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"kiratplastics_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "kiratplastics_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.stock.get_item_details.get_item_details" : "kiratplastics_erpnext.kirat_plastics_erpnext.kp_api.kp_get_item_details" 
}

fixtures = ["Custom Script", "Custom Field", "Property Setter", {"dt": "Print Format", "filters": [["name", "=", "KP Sales Invoice"]]}]