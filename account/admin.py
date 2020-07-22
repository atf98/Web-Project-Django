from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account, Worker, Company


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username',)
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user')
    search_fields = ('company_name', 'user',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Company, CompanyAdmin)
