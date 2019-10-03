from django.db import models
from django.contrib.auth.models import User


#Categories Manager

class CategoriesManager(models.Manager):

	def get_queryset(self):
		return super().get_queryset().filter(status=1)



# Create your models here.
class Categories(models.Model):

	category_name = models.CharField(max_length=30)
	image 		  = models.FileField(upload_to="category_images")
	status		  = models.IntegerField(default=1)
	created_at    = models.DateTimeField(auto_now_add=True)
	updated_at    = models.DateTimeField(auto_now=True)

	objects    = models.Manager()
	get_active = CategoriesManager()


	def __str__(self):
		return '{}'.format(self.category_name)

	def get_absolute_url(self):
	    from django.urls import reverse
	    return reverse('products:view_category', args=[str(self.id)])


class SubCategories(models.Model):

	category 	 = models.ForeignKey(Categories,related_name="sub_categories",on_delete=models.CASCADE)
	sub_category = models.CharField(max_length=30)
	image 		 = models.FileField(upload_to="subcategory_images")
	status	     = models.IntegerField(default=1)
	created_at   = models.DateTimeField(auto_now_add=True)
	updated_at   = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{}'.format(self.sub_category)


class Products(models.Model):

	user  		   = models.ForeignKey(User,related_name="user", on_delete=models.CASCADE)
	subcategory    = models.ForeignKey(SubCategories,related_name="products", on_delete=models.CASCADE)
	product_name   = models.CharField(max_length=30)
	product_id 	   = models.CharField(max_length=10)
	image  		   = models.FileField(upload_to='user_products')
	price		   = models.IntegerField()
	discount_price = models.IntegerField()
	quantity	   = models.IntegerField()
	address	   	   = models.CharField(max_length=100)
	status		   = models.IntegerField(default=1)
	created_at     = models.DateTimeField(auto_now_add=True)
	updated_at     = models.DateTimeField(auto_now=True)


	def __str__(self):
		return '{}'.format(self.product_name)


class ProductImages(models.Model):

	product    = models.ForeignKey(Products,related_name="product_images", on_delete="CASCADE")
	image 	   = models.FileField(upload_to="user_products")
	status	   = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return '{}'.format(self.product.product_name)