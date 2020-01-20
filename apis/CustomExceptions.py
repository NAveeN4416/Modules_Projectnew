from rest_framework import exceptions
from rest_framework import status
import math
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _


class CustomThrottled_Exception(exceptions.Throttled):
	status_code = status.HTTP_429_TOO_MANY_REQUESTS
	default_detail = _('Request was throttled.')
	extra_detail_singular = "Sorry!, Too many requests, limit crossed"
	extra_detail_plural = 'Sorry!, Too many requests, limit crossed'
	default_code = 'throttled'

	def __init__(self, wait=None, detail=None, throttle_instance=None):
        
		if throttle_instance is None:
			self.throttle_instance = None
		else:
			self.throttle_instance = throttle_instance

		if detail is not None:
			self.detail = force_text(detail)
		else:
			self.detail = force_text(self.default_detail)

		if wait is None:
			self.wait = None
		else:
			self.wait = math.ceil(wait)
