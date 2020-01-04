from django import template
from datetime import date,timedelta


register = template.Library()


@register.filter(name='status')
def  filter_status(value):
	if value==1:
		return 'Active'
	else:
		return 'InActive'


@register.filter(name='is_staff')
def  filter_staff(value):
	if value==1:
		return 'True'
	else:
		return 'False'


@register.filter(name="get_title")
def  get_title(value,args):

	for arg in args:
		if value is arg.id:
			return arg.name


@register.simple_tag
def define(val=None):
  return val