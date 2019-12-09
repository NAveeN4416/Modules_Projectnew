from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "products"

#Product Templates
urlpatterns = [
				#Categories
				url(r'^categories_list/', views.Categories_List, name="categories_list"),
				url(r'^delete_category/(?P<ref_id>\d+)$', views.Delete_Category, name="delete_category"),
				url(r'^view_category/(?P<ref_id>\d+)$', views.View_Category, name="view_category"),
				url(r'^edit_category/(?P<ref_id>\d+)$', views.Add_Category, name="edit_category"),
				url(r'^add_category/', views.Add_Category, name="add_category"),

				#SubCategories
				url(r'^view_subcategory/(?P<ref_id>\d+)$', views.View_SubCategory, name="view_subcategory"),
				url(r'^delete_subcategory/(?P<ref_id>\d+)$', views.Delete_SubCategory, name="delete_subcategory"),
				url(r'^edit_subcategory/(?P<category_id>\d+)/(?P<ref_id>\d+)$', views.Add_SubCategory, name="edit_subcategory"),
				url(r'^add_subcategory/(?P<category_id>\d+)$', views.Add_SubCategory, name="add_subcategory"),

				#Products
				url(r'^view_product/(?P<product_id>\d+)$', views.View_Product, name="view_product"),
				url(r'^delete_product/(?P<product_id>\d+)$', views.Delete_Product, name="delete_product"),
				url(r'^edit_product/(?P<subcategory_id>\d+)/(?P<ref_id>\d+)$', views.Add_Product, name="edit_product"),
				url(r'^add_product/(?P<subcategory_id>\d+)/$', views.Add_Product, name="add_product"),
				url(r'^products_list/', views.Products_List, name="products_list"),
			]