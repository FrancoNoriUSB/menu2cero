from django import template

register = template.Library()

#Tag de template para obtener el url
@register.simple_tag
def active_page(request, view_name):
    from django.core.urlresolvers import resolve, Resolver404
    if not request:
        return ""
    try:
        return "active" if resolve(request.path_info).url_name == view_name else ""
    except Resolver404:
        return ""


#Tag para encontrar el siguiente valor en un for
@register.filter(name='next')
def next(value, arg):
    try:
        return value[int(arg)+1]
    except:
        return None