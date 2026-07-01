from django.contrib import admin
from .models import FeeItem, Payment

@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'student_name', 'amount', 'status', 'due_date', 'parent']
    list_filter = ['status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'amount', 'status', 'parent', 'created_at']
    list_filter = ['status']


from .models import SavedCard

@admin.register(SavedCard)
class SavedCardAdmin(admin.ModelAdmin):
    list_display = ['card_holder_name', 'card_type', 'last_four', 'is_default', 'parent']    