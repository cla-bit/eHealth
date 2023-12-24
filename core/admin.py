from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import CustomUser, HealthWorker, Patient, Appointment

# Register your models here.


class CustomUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    search_fields = ('email', 'phone_number')
    list_display = ('email', 'phone_number', 'is_worker')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'phone_number', 'position', 'password')}),
        ('Permissions', {'fields': ('is_worker', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'position', 'is_worker',
                       'password1', 'password2', 'groups', 'user_permissions',
                       'is_staff', 'is_active'),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Save the CustomUser model
        super().save_model(request, obj, form, change)

        if obj.is_worker:
            # If the user is a teacher, add them to the "Teachers" group
            worker, created = Group.objects.get_or_create(name='Health Worker')
            obj.groups.add(worker)
        else:
            # If the user is not a teacher, remove them from the "Teachers" group
            worker = Group.objects.get(name='Health Worker')
            obj.groups.remove(worker)


@admin.register(HealthWorker)
class HealthWorkerAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    list_filter = ('user', 'department')
    search_fields = ('user__username', 'user__email', 'user__phone_number')

    def save_model(self, request, obj, form, change):
        # Add the teacher to the 'Instructors' group
        worker = Group.objects.get(name='Health Worker')
        obj.user.groups.add(worker)
        super().save_model(request, obj, form, change)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'blood_group', 'weight', 'height', 'is_diabetic')
    list_filter = ('user',)
    search_fields = ('user__username', 'user__email', 'user__phone_number')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'worker', 'date', 'time', 'status')
    list_filter = ('patient', 'worker', 'date', 'time', 'status')
    search_fields = ('patient__user__username', 'patient__user__email', 'patient__user__phone_number',
                     'worker__user__username', 'worker__user__email', 'worker__user__phone_number')


admin.site.register(CustomUser, CustomUserAdmin)
