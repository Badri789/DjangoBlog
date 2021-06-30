from django import template
from blog.models import Notification, Tag

register = template.Library()


@register.inclusion_tag('partials/show_notifications.html', takes_context=True)
def show_notifications(context):
    request_user = context['request'].user

    notifications = Notification.objects.filter(to_user=request_user).order_by('-date')[:10]
    not_seen_count = Notification.objects.filter(to_user=request_user).exclude(user_has_seen=True).count

    return {
        'notifications': notifications,
        'not_seen_count': not_seen_count,
        'username': request_user.username
    }


@register.inclusion_tag('partials/show_categories.html')
def show_categories():
    categories = Tag.objects.all()

    return {
        'categories': categories
    }


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
