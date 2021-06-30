from django.conf import settings
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.utils.text import slugify
from ckeditor.fields import RichTextField


class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(validators=[MinLengthValidator(30)], max_length=100)
    date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=100)
    header_image = models.ImageField(upload_to='posts_header_images/', blank=False)
    body = RichTextField(validators=[MinLengthValidator(500)])
    tags = models.ManyToManyField(Tag)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        # image = Image.open(self.header_image.path)
        # print(image)
        # image.save(self.header_image.path, quality=30, optimize=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    body = models.TextField(validators=[MinLengthValidator(15)])
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    root_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='sub_comments')

    def __str__(self):
        return f'Comment: {self.id} on post: {self.post.title}'


class PostRating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    liked = models.BooleanField()

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'Post: {self.post.title} - Liked: {self.liked}'


class Notification(models.Model):
    # 1) Users Post Liked, 2 ) User Post Disliked
    # 3) User Post Commented, 4) Comment Reply
    type = models.IntegerField()
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='notification_to', null=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='notification_from', null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification: {self.id} - from {self.from_user} to {self.to_user}'
