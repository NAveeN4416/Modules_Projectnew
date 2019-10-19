from django.db import models


def replace(self):
	return self.name.lower().replace(' ', '_')



def directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    path = "industries"

    if isinstance(instance,Artist):
    	path = f"{path}/{repr(instance.industry)}"


    if isinstance(instance,Album):
    	path = f"{path}/{repr(instance.artist.industry)}/{repr(instance.artist)}"

    if isinstance(instance,Track):
    	return f"{path}/{repr(instance.album.artist.industry)}/{repr(instance.album.artist)}/{repr(instance.album)}/{filename}"

    return f"{path}/{repr(instance)}/{filename}"

    


# Create your models here.
class Industry(models.Model):
	name  		= models.CharField(max_length=50)
	image       = models.FileField(upload_to=directory_path)
	created_at	= models.DateTimeField(auto_now_add=True)
	updated_at	= models.DateTimeField(auto_now=True)

	__repr__ = replace

	def __str__(self):
		return f"{self.name.title()} - Industry"


class Artist(models.Model):
	name 		= models.CharField(max_length=30)
	image       = models.FileField(upload_to=directory_path)
	industry    = models.ForeignKey(Industry,related_name="artists",on_delete=models.CASCADE)
	dob  		= models.DateField(blank=True,null=True)
	created_at	= models.DateTimeField(auto_now_add=True)
	updated_at	= models.DateTimeField(auto_now=True)


	__repr__ = replace


	def __str__(self):
		return f"{self.name.title()} - Artist"


class Album(models.Model):
	name   	   = models.CharField(max_length=50)
	image      = models.FileField(upload_to=directory_path)
	movie  	   = models.CharField(max_length=50,blank=True)
	artist 	   = models.ForeignKey(Artist, related_name="albums",on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	__repr__ = replace

	def __str__(self):
		return f"{self.name.title()} - Album"


class Track(models.Model):
	name   	   = models.CharField(max_length=50)
	album  	   = models.ForeignKey(Album,related_name="tracks",on_delete=models.CASCADE)
	file       = models.FileField(upload_to=directory_path)
	length 	   = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	__repr__ = replace

	def __str__(self):
		return f"{self.name.title()} - Track"



