from logging import log

from django.contrib import admin

from .enums import TransactionStatuses
from .models import Wallet, WalletTransaction, Charge, Transfer
from .services import decline_charge_service, approve_charge_service


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "name", "is_active", "balance_display", "created_at")
    readonly_fields = ("owner", "name", "is_active", "created_at", "updated_at")

    def balance_display(self, obj):
        return obj.balance
    balance_display.short_description = "Balance"

    def has_add_permission(self, request):
        return False

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "type", "status", "amount", "created_at")
    readonly_fields = list_display
    list_filter = ("type", "status")
    search_fields = ("wallet__owner__username",)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ("id", "wallet", "amount", "status", "created_at", "processed_at")
    list_filter = ("status",)
    actions = ["approve_charges", "decline_charges"]

    def approve_charges(self, request, queryset):
        for charge in queryset.filter(status=TransactionStatuses.PENDING.value):
            try:
                approve_charge_service(charge)
                self.message_user(request, f"Charge {charge.id} approved.")
            except Exception as e:
                self.message_user(request, f"Error approving charge {charge.id}: {e}", level="error")
                print(e)
    approve_charges.short_description = "Approve selected charges"

    def decline_charges(self, request, queryset):
        for charge in queryset.filter(status=TransactionStatuses.PENDING.value):
            try:
                decline_charge_service(charge)
                self.message_user(request, f"Charge {charge.id} declined.")
            except Exception as e:
                self.message_user(request, f"Error declining charge {charge.id}: {e}", level="error")
    decline_charges.short_description = "Decline selected charges"

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("id", "source_wallet", "target_wallet", "amount", "status", "created_at", "processed_at")
    list_filter = ("status",)
    search_fields = ("source_wallet__owner__username", "target_wallet__owner__username")
    ordering = ("-created_at",)
