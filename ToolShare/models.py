from django.db import models
import uuid
from django.contrib.auth.models import User
import os
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import datetime

import accounts.models


def make_uuid():
    return str(uuid.uuid1().int >> 64)


class Category(models.Model):
    cat_id = models.CharField(max_length=36, primary_key=True, default=make_uuid)
    value = models.CharField(max_length=30)

    def __unicode__(self):
        return self.value


class Tool(models.Model):
    """
    Creates the model of the Tool object(s).
    """
    tid = models.CharField(max_length=36, primary_key=True, default=make_uuid, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.ForeignKey(accounts.models.Locations)
    owner = models.ForeignKey(User, related_name='owner')
    status = models.CharField(max_length=10)
    rating = models.DecimalField(decimal_places=2, max_digits=3,
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(5)])
    checkout = models.CharField(max_length=36, blank=True, null=True)
    request = models.BooleanField(default=False)
    category = models.ForeignKey(Category, null=True)

    def make_tpic_filename(self, filename):
        """
        Create the filename from the Tool image.
        """
        file_extension = os.path.splitext(filename)[len(filename.split('.')) - 1].lower()
        # Since the prevention of the use of models.ImageField, there has be some crude file validation
        if file_extension == (".jpeg" or ".jpe" or ".jif" or ".jfif" or ".jfi"):
            file_extension = ".jpg"

        if file_extension == ".tiff":
            file_extension = ".tif"

        if file_extension != (".jpg" or ".png" or ".bmp" or ".gif" or ".tif"):
            print('Unsupported Image Type')
            return "uploaded_images/tools/garbage/" + str(self.tid) + file_extension
        new_filename = "uploaded_images/tools/" + str(self.tid) + file_extension

        # If there exists a file with the same name, delete it.
        if os.path.isfile(new_filename):
            os.remove(new_filename)
        return new_filename
    pic = models.FileField("Tool Picture", upload_to=make_tpic_filename, blank=True, null=True)

    def equals(cmpTool):
        """
        Check if two tools are equal via the unique identifiers.
        """
        if cmpTool.tid == Tool.tid:
            return True
        else:
            return False

    def __str__(self):
        return str(self.tid)


class Checkout(models.Model):
    """
    Creates the model of the Checkout object(s).
    """
    cid = models.CharField(max_length=36, primary_key=True, default=make_uuid)
    uid = models.ForeignKey(User, related_name='uid')
    tool = models.ForeignKey(Tool, related_name='tool')
    time_out = models.DateTimeField(default=timezone.now())
    time_in = models.DateTimeField(default=timezone.now())
    approved = models.BooleanField(default=False)
    rating = models.DecimalField(decimal_places=2, max_digits=3,
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(5)], blank=True, null=True)
    review = models.TextField(blank=True, null=True)


