from rest_framework import viewsets
from .CustomExceptions import CustomThrottled_Exception

class ThrottledViewSet(viewsets.ModelViewSet):
    """
    Adds customizability to the throtted method for better clarity.
    """

    throttled_exception_class = CustomThrottled_Exception

    def throttled(self, request, wait, throttle_instance=None):
        """
        If request is throttled, determine what kind of exception to raise.
        """
        raise self.get_throttled_exception_class()(wait, detail=self.get_throttled_message(request),
                                                   throttle_instance=throttle_instance)

    def get_throttled_message(self, request):
        """
        Add a custom throttled exception message to pass to the user.
        Note that this does not account for the wait message, which will be added at the
        end of this message.
        """
        return None

    def get_throttled_exception_class(self):
        """
        Return the throttled exception class to use.
        """
        return self.throttled_exception_class

    def check_throttles(self, request):
            """
            Check if request should be throttled.
            Raises an appropriate exception if the request is throttled.
            """
            for throttle in self.get_throttles():
                if not throttle.allow_request(request, self):
                    self.throttled(request, throttle.wait(), throttle_instance=throttle)