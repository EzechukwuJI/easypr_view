from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()



@register.filter
def strip_chars(value, char):
	return value.replace(char, " ")


@register.filter
def is_even(number):
	''' returns true or false for even or odd number '''
	return number % 2 == 0