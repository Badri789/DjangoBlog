from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import Post, Comment
from ckeditor.fields import RichTextField


class PostForm(forms.ModelForm):
    body = RichTextField()

    class Meta:
        model = Post
        exclude = ['date', 'slug', 'created_by']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-title',  # შეგვიძლია id არ დავუწეროთ input-ებს და ავტომატურად აგენერირებს
                'placeholder': 'Enter Post Title...'
            }),

            'header_image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'input-image'
            }),

            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'input-text'
            }),

            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            })
        }

        labels = {
            'title': 'Post Title',
            'body': 'Post Body',
            'header_image': 'Post Header Image',
            'tags': 'Post Tags'
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''

        if self.errors:
            for error in dict(self.errors):
                if error != 'body':
                    self.fields[error].widget.attrs['class'] += ' is-invalid'

    def clean_header_image(self):
        image = self.cleaned_data.get('header_image')
        limit_kb = 500
        min_width = 750
        min_height = 300

        image_size = image.size
        width, height = get_image_dimensions(image)

        if image_size > limit_kb * 1024:
            raise ValidationError(f'Maximum size of the post header image is {limit_kb} KB.')
        elif width < min_width or height < min_height:
            raise ValidationError(
                f'Ensure that image width is at least {min_width}px and height is at least {min_height}px.'
            )

        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            }),
        }

        labels = {
            'body': 'Add Comment'
        }
