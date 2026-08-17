from django.contrib import admin
from . models import CustomUser, TermsOfService, PrivacyPolicy, PlacementQuestion
# Register your models here.


admin.site.register(CustomUser)
admin.site.register(TermsOfService)
admin.site.register(PrivacyPolicy)
admin.site.register(PlacementQuestion)