#!/usr/bin/env python3

"""This module contains custom exceptions that are raised by diaspy.
These are not described by DIASPORA* protocol as exceptions that should be
raised by API implementations but are specific to this particular implementation.

If your program should catch all exceptions raised by diaspy and
does not need to handle them specifically you can use following code:

    # this line imports all errors
    from diaspy.errors import *

    try:
        # your code...
    except DiaspyError as e:
        # your error handling code...
    finally:
        # closing code...
"""

import warnings


class DiaspyError(Exception):
    """Base exception for all errors
    raised by diaspy.
    """
    pass


class LoginError(DiaspyError):
    """Exception raised when something
    bad happens while performing actions
    related to logging in.
    """
    pass


class TokenError(DiaspyError):
    pass


class UserError(DiaspyError):
    """Exception raised when something related to users goes wrong.
    """
    pass


class InvalidHandleError(DiaspyError):
    """Raised when invalid handle is found.
    """
    pass


class SearchError(DiaspyError):
    """Exception raised when something related to search goes wrong.
    """
    pass


class ConversationError(DiaspyError):
    """Exception raised when something related to conversations goes wrong.
    """
    pass


class AspectError(DiaspyError):
    """Exception raised when something related to aspects goes wrong.
    """
    pass


class PostError(DiaspyError):
    """Exception raised when something related to posts goes wrong.
    """
    pass


class StreamError(DiaspyError):
    """Exception raised when something related to streams goes wrong.
    """
    pass


class SettingsError(DiaspyError):
    """Exception raised when something related to settings goes wrong.
    """
    pass


def react(r, message='', accepted=[200, 201, 202, 203, 204, 205, 206], exception=DiaspyError):
    """This method tries to decides how to react
    to a response code passed to it. If it's an
    error code it will raise an exception (it will
    call `throw()` method.

    If response code is not accepted AND cannot
    be matched to any exception, generic exception
    (DiaspyError) is raised (provided that `exception`
    param was left untouched).

    By default `accepted` param contains all HTTP
    success codes.

    User can force type of exception to raise by passing
    `exception` param.

    :param r: response code
    :type r: int
    :param message: message for the exception
    :type message: str
    :param accepted: list of accepted error codes
    :type accepted: list
    :param exception: preferred exception to raise
    :type exception: valid exception type (default: DiaspyError)
    """
    warnings.warn(DeprecationWarning)
    if r in accepted: e = None
    else: e = DiaspyError

    if e is not None: e = exception
    throw(e, message=message)


def throw(e, message=''):
    """This function throws an error with given message.
    If None is passed as `e` throw() will not raise
    anything.

    :param e: exception to throw
    :type e: any valid exception type or None
    :param message: message for exception
    :type message: str
    """
    warnings.warn(DeprecationWarning)
    if e is None: pass
    else: raise e(message)
