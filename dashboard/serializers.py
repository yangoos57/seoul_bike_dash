from rest_framework import serializers
from .models import *


class stationInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = stationInformation
        fields = ["st_id", "st_name"]


class selector_OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = selector_Options
        fields = "__all__"
