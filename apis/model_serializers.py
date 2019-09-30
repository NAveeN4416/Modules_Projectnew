from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserDetails
from products.models import Categories, SubCategories, Products, ProductImages


# Serializers define the API representation.
class UserSerializer(serializers.Serializer):

	username     = serializers.CharField(max_length=150)
	first_name   = serializers.CharField(max_length=30)
	last_name    = serializers.CharField(max_length=150)
	email        = serializers.EmailField(max_length=254)
	password     = serializers.CharField(max_length=254)
	is_staff     = serializers.HiddenField(default=False)
	is_active    = serializers.HiddenField(default=False)
	date_joined  = serializers.DateTimeField(required=False,read_only=True,format="%d, %b %Y")


	def create(self, validated_data):
		return User.objects.create_user(**validated_data)


	def update(self, instance, validated_data):
		instance.username   = validated_data.get('email',instance.email)
		instance.first_name = validated_data.get('first_name',instance.first_name)
		instance.last_name  = validated_data.get('last_name',instance.last_name)
		instance.is_staff   = validated_data.get('is_staff',instance.is_staff)
		instance.is_active  = validated_data.get('email',instance.is_active)
		instance.save()
		return instance


# Serializers define the API representation.
class UserMSerializer(serializers.ModelSerializer):

	date_joined = serializers.DateTimeField(format="%d, %b %Y")

	class Meta:
	 	model  = User
	 	fields = ['username','first_name','last_name','email','date_joined'] #'__all__' #


class UserdetailsSerializer(serializers.ModelSerializer):

	class Meta:
		model  = UserDetails
		fields = ['image','phone_number','address','device_type','device_token','role']


class ProductsSerializer(serializers.ModelSerializer):

	user = UserMSerializer(read_only=True)
	created_at = serializers.DateTimeField(format="%d, %b %Y")

	class Meta:
		model  = Products
		fields = ['id','user','product_name','product_id','image','price','discount_price','quantity','address','created_at']


class SubCategorySerializer(serializers.ModelSerializer):

	created_at = serializers.DateTimeField(format="%d, %b %Y")
	products   = ProductsSerializer(many=True, read_only=True)

	class Meta:
		model  = SubCategories
		fields = ['id','sub_category','image','created_at','products']



class CategorySerializer(serializers.ModelSerializer):

	sub_categories = SubCategorySerializer(many=True, read_only=True)
	created_at 	   = serializers.DateTimeField(format="%d, %b %Y")
	#image          = serializers.FileField(use_url=True)
	#image_url      = serializers.SerializerMethodField()

	class Meta:
		model  = Categories
		fields = ['id','category_name','image','created_at','sub_categories']


	def get_image_url(self, obj):
		return obj.image.url