from django.core.exceptions import ValidationError
import re


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if re.search('[A-Z]', password) is None or re.search('[0-9]', password) is None or \
                re.search('[^A-Za-z0-9]', password) is None:
            raise ValidationError(
                'Your password must contain at least 1 number, 1 uppercase and 1 non-alphanumeric character.'
            )

    def get_help_text(self):
        return 'Your password must contain at least 1 number, 1 uppercase and 1 non-alphanumeric character.'
