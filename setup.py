# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pip.req import parse_requirements

version = '1.0.8'
requirements = parse_requirements("requirements.txt", session="")

setup(
	name='kiratplastics_erpnext',
	version=version,
	description='ERPNext extensions for Kirat Plastics Pvt. Ltd.',
	author='MN Technique',
	author_email='support@castlecraft.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[str(ir.req) for ir in requirements],
	dependency_links=[str(ir._link) for ir in requirements if ir._link]
)
