from rest_framework.views import exception_handler
from rest_framework import status
from django.http import JsonResponse
from django.utils.translation import gettext
from rest_framework.exceptions import ValidationError, ErrorDetail


def chessmatch_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data = _process_error(response.data, exc)

        if isinstance(exc, ValidationError):
            """ Ошибка валидации - 422 """
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return response


def _process_error(error_data, exc):
    result = {
        'errors': [],
    }

    def process_error_detail(error, key=None, exc=None):
        error_tmp = {
            'detail': error,
            'code': error.code,
        }

        if exc and isinstance(exc, ValidationError):
            """ Ошибка валидации """
            error_tmp['inner_error'] = {'validated_field': key}
        elif hasattr(exc, 'inner_error'):
            error_tmp['inner_error'] = exc.inner_error

        return error_tmp

    def recursive_step(data, key, exc, step):
        step += 1

        if step > 2:
            return process_error_detail(ErrorDetail('Exception parse error', 'exception_parse_error'))

        if isinstance(data, ErrorDetail):
            return process_error_detail(data, key, exc)
        else:
            for subdata in data:
                if isinstance(subdata, ErrorDetail):
                    return process_error_detail(subdata, key, exc)
                elif isinstance(subdata, dict):
                    for subkey in subdata:
                        return recursive_step(subdata[subkey], subkey, exc, step)
                else:
                    for subsubdata in data[subdata]:
                        return recursive_step(subsubdata, subdata, exc, step)

    if isinstance(error_data, list):
        for error_data_detail in error_data:
            for key in error_data_detail:
                if isinstance(key, ErrorDetail):
                    result['errors'].append(
                        process_error_detail(key, None, exc)
                    )
                else:
                    result['errors'].append(
                        recursive_step(error_data_detail[key], key, exc, 0)
                    )
    else:
        for key in error_data:
            result['errors'].append(
                recursive_step(error_data[key], key, exc, 0)
            )

    return result

def bad_request_view(request, exception=None):
    """
    Generic 400 error handler.
    """
    data = {
        'errors': [{
            'detail': gettext('Bad request.'),
            'code': status.HTTP_400_BAD_REQUEST,
        }]
    }
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def permission_denied_view(request, exception, *args, **kwargs):
    """
    Generic 403 error handler.
    """
    data = {
        'errors': [{
            'detail': gettext('Permission_denied.'),
            'code': 'permission_denied',
        }]
    }
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)


def page_not_found_view(request, exception, *args, **kwargs):
    """
    Generic 404 error handler.
    """
    data = {
        'errors': [{
            'detail': gettext('Not found.'),
            'code': 'not_found',
        }]
    }
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)


def server_error_view(request, exception=None):
    """
    Generic 500 error handler.
    """
    data = {
        'errors': [{
            'detail': gettext('Internal server error.'),
            'code': 'internal_server_error',
        }]
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
