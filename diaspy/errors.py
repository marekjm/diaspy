#!/usr/bin/env python3


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
    if e is None: pass
    else: raise e(message)
