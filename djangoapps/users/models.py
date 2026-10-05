from PIL import Image

from django.db import models
from django.contrib.auth.models import AbstractUser

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("NB", "Non-binary"),
    ("O", "Other"),
    ("-", "Prefer Not To Say")
]


class User(AbstractUser):  # custom user model defined here
    ''' our custom user model for our website

        note: spotify autogenerates usernames for its registered users
        hence our model will be following a similar approach'''
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    profile_name = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        default="-",  # prefer not to say
    )
    profile_photo = models.ImageField(
        default='default.jpg',
        upload_to='profile_photo')
    is_artist = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'password', 'profile_name', 'date_of_birth',
                       'gender']

    def __str__(self):
        return self.profile_name

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.profile_photo.path)
        width, height = img.size

        if height > 400 or width > 400 or width != height:
            # crop the image
            if width == height:
                resized_image = img
            offset = int(abs(height-width)/2)
            if width > height:
                resized_image = img.crop([offset, 0, width-offset, height])
            else:
                resized_image = img.crop([0, offset, width, height-offset])

            # resize image and save
            output_size = (400, 400)
            resized_image.thumbnail(output_size)
            resized_image.save(self.profile_photo.path)
