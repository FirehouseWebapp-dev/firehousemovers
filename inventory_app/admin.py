from django.contrib import admin
from inventory_app.models import UniformCatalog,UniformAssignment,Inventory,InventoryTransaction


class UniformCatalogAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'gender', 'minimum_stock_level']
    search_fields = ['name', 'category']
    list_filter = ['category', 'gender']

class UniformAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'uniform', 'condition', 'quantity','status','date']
    search_fields = ['employee', 'uniform','condition']
    list_filter = ['condition', 'status']

class InventoryAdmin(admin.ModelAdmin):
    list_display = ['uniform', 'new_stock', 'used_stock','in_use','disposed','return_to_supplier','total_bought']
    search_fields = ['uniform']
    list_filter = ['uniform']

class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'uniform','quantity','condition']
    search_fields = ['transaction_type','uniform','condition']
    list_filter = ['transaction_type','condition']

admin.site.register(UniformCatalog,UniformCatalogAdmin)
admin.site.register(UniformAssignment,UniformAssignmentAdmin)
admin.site.register(Inventory,InventoryAdmin)
admin.site.register(InventoryTransaction,InventoryTransactionAdmin)

