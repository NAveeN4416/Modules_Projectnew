from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "products"

#Product Templates
urlpatterns = [
				#Categories
				url(r'^categories_list/', views.Categories_List, name="categories_list"),
				url(r'^delete_category/(?P<ref_id>\d+)$', views.Delete_Category, name="delete_category"),
				url(r'^add_category/(?P<ref_id>\d+)$', views.Add_Category, name="add_category"),
				url(r'^add_category/', views.Add_Category, name="add_category"),

				#SubCategories
				url(r'^subcategories_list/', views.SubCategories_list, name="subcategories_list"),
				url(r'^add_subcategory/(?P<ref_id>\d+)$', views.Add_SubCategory, name="add_subcategory"),
				url(r'^add_subcategory/', views.Add_SubCategory, name="add_subcategory"),

				#Products
				url(r'^products_list/', views.Products_List, name="products_list"),
				url(r'^add_product/', views.Add_Product, name="add_product"),
			]