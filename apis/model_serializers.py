from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserDetails



# Serializers define the API representation.
class UserSerializer(serializers.Serializer):

	username     = serializers.CharField(max_length=150)
	first_name   = serializers.CharField(max_length=30)
	last_name    = serializers.CharField(max_length=150)
	email        = serializers.EmailField(max_length=254)
	password     = serializers.CharField(max_length=254)
	is_staff     = serializers.BooleanField ()
	is_active    = serializers.BooleanField ()
	date_joined  = serializers.DateTimeField()

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

	class Meta:
	 	model = User
	 	fields = ['username','first_name','last_name','email','is_staff','is_active','date_joined'] #'__all__' #


class UserdetailsSerializer(serializers.ModelSerializer):

	class Meta:
		model  = UserDetails
		fields = ['image','phone_number','address','device_type','device_token','role']