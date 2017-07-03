from django.contrib import admin
from .models import Sage


class SageAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_token_expires_on', 'refresh_token_expires_on']
    readonly_fields = ['access_token_key', 'access_token_type', 'access_token_expires_on',
                       'refresh_token', 'refresh_token_expires_on']
admin.site.register(Sage, SageAdmin)
