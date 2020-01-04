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

	def validate_username(self,value):

		if value != 'Testing10234':
			raise serializers.ValidationError("Username should be different")
		return value


class UserdetailsSerializer(serializers.ModelSerializer):

	#image = serializers.FileField(use_url=True)

	class Meta:
		model  = UserDetails
		fields = ['image','phone_number','address','device_type','device_token','role','user_id']


	def create(self,validated_data):
		user_details = UserDetails(**validated_data)
		user_details.save()
		return user_details


	def update(self,instance,validated_data):
		userdetails = UserDetails.objects.filter(user=instance.user_id)
		userdetails.update(**validated_data)
		return UserDetails.objects.get(user=instance.user_id)



# Serializers define the API representation.
class UserMSerializer(serializers.ModelSerializer):

	#first_name   = serializers.CharField(max_length=10,required=True)
	user_details = UserdetailsSerializer(read_only=True)
	date_joined  = serializers.DateTimeField(format="%d, %b %Y")
	email 		 = serializers.EmailField(required=True)
	#groups = serializers.StringRelatedField(many=True,read_only=True)
	#user_permissions = serializers.StringRelatedField(many=True,read_only=True)

	class Meta:
	 	model  = User
	 	fields = ['id','username','password','first_name','last_name','email','date_joined','user_details'] #'__all__' #
	 	#fields = '__all__'
	 	extra_kwargs = {'password': {'write_only': True}}


	def create(self,validated_data):
		password = validated_data.pop('password',None)
		user = User(**validated_data)
		user.set_password(password)
		user.save()
		return user

	def update(self,instance,validated_data):
		user = User.objects.filter(id=instance.pk)
		user.update(**validated_data)
		return User.objects.get(id=instance.pk)


class ProductImages(serializers.ModelSerializer):

	class Meta:
		model = ProductImages
		fields = ['image']


class ProductsSerializer(serializers.ModelSerializer):

	user = UserMSerializer()
	product_images = ProductImages(many=True,read_only=True)
	created_at = serializers.DateTimeField(format="%d, %b %Y")

	class Meta:
		model  = Products
		fields = ['id','product_name','product_id','image','price','discount_price','quantity','address','created_at','product_images','user']


class SubCategorySerializer(serializers.ModelSerializer):

	created_at = serializers.DateTimeField(format="%d, %b %Y")
	products   = ProductsSerializer(many=True)

	class Meta:
		model  = SubCategories
		fields = ['id','sub_category','image','created_at','products']


class CategorySerializer(serializers.ModelSerializer):

	sub_categories = SubCategorySerializer(many=True, read_only=True)
	created_at 	   = serializers.DateTimeField(format="%d, %b %Y")
	image          = serializers.FileField(use_url=True)
	image_url      = serializers.SerializerMethodField()

	class Meta:
		model  = Categories
		fields = ['id','category_name','image','created_at','sub_categories','image','image_url']


	def get_image_url(self, obj):
		return obj.image.url