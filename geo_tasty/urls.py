from django.contrib import admin
from django.urls import path, include

from tastypie.api import Api
from shops.api import UserRegisterResource, UserSetPointResource, ShopsInUserRadiusResource


api_v1 = Api(api_name='v1')
api_v1.register(UserRegisterResource())
api_v1.register(UserSetPointResource())
api_v1.register(ShopsInUserRadiusResource())


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_v1.urls)),
]
