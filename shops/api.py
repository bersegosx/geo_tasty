from django import forms
from django.db import IntegrityError
from django.conf.urls import url
from django.contrib.gis.db.models.functions import Distance as DistanceFunc
from django.contrib.gis.measure import Distance

from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication
from tastypie.contrib.gis.resources import ModelResource
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest

from .models import Shop, User


class AnonymUserCreationAuth(ReadOnlyAuthorization):

    def create_detail(self, object_list, bundle):
        return True


class UserRegisterForm(forms.Form):

    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)


class UserRegisterResource(ModelResource):
    class Meta:
        resource_name = 'register'
        authorization = AnonymUserCreationAuth()

        object_class = User
        fields = ['username', 'password']
        list_allowed_methods = ['post']
        detail_allowed_methods = []

        queryset = User.objects.all()
        validation = FormValidation(form_class=UserRegisterForm)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(UserRegisterResource, self).obj_create(bundle)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('Username already exists')

        return bundle


class UserSetPointResource(ModelResource):
    class Meta:
        resource_name = 'user/set_point'
        authorization = Authorization()
        authentication = BasicAuthentication()

        object_class = User
        queryset = User.objects.all()
        fields = ['point']

        list_allowed_methods = []
        detail_allowed_methods = ['patch']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'),
                 name="api_dispatch_detail"),
        ]


class ShopsInUserRadiusResource(ModelResource):
    class Meta:
        resource_name = 'shop/by_radius'
        authorization = Authorization()
        authentication = BasicAuthentication()

        object_class = Shop
        list_allowed_methods = ['get']
        detail_allowed_methods = []

    def get_object_list(self, request):
        if not request.user.point:
            raise BadRequest("User doesn't set point")
        return self.get_nearby_shops(request.user.point)

    def get_nearby_shops(self, user_point, radius_km=5, limit=20):
        result = Shop.objects \
            .filter(point__distance_lte=(user_point, Distance(km=radius_km))) \
            .annotate(distance=DistanceFunc('point', user_point)) \
            .order_by('distance')[:limit]

        return result
