from functools import wraps
from flask import g, url_for, request, redirect


def require_openid(f):
    """Require user to be logged in."""
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.user is None:
            next_url = url_for("login") + "?next=" + request.url
            return redirect(next_url)
        else:
            return f(*args, **kwargs)
    return decorator
