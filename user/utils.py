from django.contrib.auth.decorators import user_passes_test

def specific_superuser_required(username):
    """
    Decorator for views that checks that the user is a specific superuser.
    """
    def decorator(view_func):
        @user_passes_test(lambda user: user.is_superuser and user.username == 'mutuku')
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
