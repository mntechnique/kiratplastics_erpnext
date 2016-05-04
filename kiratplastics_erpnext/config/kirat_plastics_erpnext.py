from frappe import _

def get_data():
	return [
		{
			"label": _("Setup"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Excise Chapter",
					"description": _("Excise Chapters"),
				}
			]
		},
		{
			"label": _("Excise Chapter Chart"),
			"icon": "icon-list",
			"items": [
				{
					"type": "page",
					"name": "excise-chapter-chart",
					"label": _("Excise Chapter Chart"),
				},
			]
		},
	]
