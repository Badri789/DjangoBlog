from django.contrib import admin
from .models import Post, Tag, Comment, PostRating, Notification


class PostAdmin(admin.ModelAdmin):
    # ადმინ პანელში რომ slug ავტომატურად შეივსოს title-ის შევსებასთან ერთად
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(PostRating)
admin.site.register(Notification)
