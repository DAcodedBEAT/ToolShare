import os
from django.db import models
from django.contrib.auth.models import User
import uuid
import math


def make_uuid():
    """
    Makes a unique integer identifier
    """
    return str(uuid.uuid1().int >> 64)


class Locations(models.Model):
    """
    Creates the model of the Location object(s).
    """
    loc_id = models.CharField(max_length=36, primary_key=True, default=make_uuid)  # The ID of the Location
    user = models.ForeignKey(User)
    address = models.TextField(null=False)
    location = models.CharField(max_length=36, null=False)
    default = models.BooleanField(default=False)

    def getDistance(self, input):
        """
        Gets the distance between two locations.
        """
        cords = self.location.split(',')
        lat_a = float(cords[0])
        lng_a = float(cords[1])
        cords_b = input.split(',')
        lat_b = float(cords_b[0])
        lng_b = float(cords_b[1])

        R = 6371
        dLat = math.radians(lat_b-lat_a)
        dLon = math.radians(lng_b-lng_a)
        lat1 = math.radians(lat_a)
        lat2 = math.radians(lat_b)

        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        theD = round(R * c, 4)
        return theD

    def compareDistance(self, input, distance=10):
        """
        Compares the distance between 2 locations.
        """
        dist = self.getDistance(input)
        if dist >= distance:
            return False
        else:
            return True

    def __unicode__(self):
        return self.address

    def __str__(self):
        return self.address + " (" + str(self.user.username) + ")"

    class Meta:
        verbose_name_plural = "locations"


class UserProfile(models.Model):
    """
    Creates the model of the UserProfile object(s).
    """
    user = models.OneToOneField(User, parent_link=True)
    location = models.ForeignKey(Locations, null=True, blank=False)
    phone_number = models.CharField(max_length=10, null=True, blank=True)

    def make_upic_filename(self, filename):
        """
        Creates the filename for the profile image.
        """
        file_extension = os.path.splitext(filename)[len(filename.split('.')) - 1].lower()
        print(file_extension)
        # Since the prevention of the use of models.ImageField, there has be some crude file validation
        if file_extension == (".jpeg" or ".jpe" or ".jif" or ".jfif" or ".jfi"):
            file_extension = ".jpg"
        if file_extension == ".tiff":
            file_extension = ".tif"
        if file_extension != (".jpg" or ".png" or ".bmp" or ".gif" or ".tif"):
            print('Unsupported File Type!!!!')
            return "uploaded_images/users/garbage/" + self.user.username + file_extension
        new_filename = "uploaded_images/users/" + self.user.username + file_extension

        # If there exists a file with the same name, delete it.
        if os.path.isfile(new_filename):
            os.remove(new_filename)
        return new_filename

    pic = models.FileField("Profile Picture", upload_to=make_upic_filename, blank=True, null=True)

    def __str__(self):
        return self.user.username


## Workaround
def makeOrGetUserProfile(user):
    if len(UserProfile.objects.filter(user=user)) != 0:
        return UserProfile.objects.get(user=user)
    else:
        return UserProfile.objects.get_or_create(user=user, location_id=make_uuid())[0]

User.profile = property(lambda usr: makeOrGetUserProfile(usr))