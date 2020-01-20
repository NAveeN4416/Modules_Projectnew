from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, MethodNotAllowed
from .CustomExceptions import CustomThrottled_Exception


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,

    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc,CustomThrottled_Exception):
    	response_data =	{
                            'status': response.status_code,
                            'message': "Sorry Request limit crossed !",
                            'data': {}
                        };
    	response.data = response_data


    if isinstance(exc,MethodNotAllowed):
        response_data = {
                            'status': response.status_code,
                            'message': f"This method not allowed for this API",
                            'data': {}
                        };

        response.data = response_data


    if isinstance(exc,PermissionDenied):
        response_data = {
                            'status': response.status_code,
                            'message': "You don't have permissions for this action",
                            'data': {}
                        };
        response.data = response_data


    if isinstance(exc,AuthenticationFailed):
        if response is not None:
            response.data['status_code'] = response.status_code


    return response