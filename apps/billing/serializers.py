from rest_framework import serializers

from .enums import TransactionStatuses
from .models import WalletTransaction, Charge, Transfer, Wallet


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Wallet
        fields = "__all__"
        read_only_fields = ("id","owner",'is_active')

    def create(self, validated_data):
        user = self.context["request"].user
        return Wallet.objects.create(owner=user, **validated_data)

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = "__all__"

class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "wallet_transaction",
            "created_at",
            "processed_at",
        )

    # limit writable fields on input
    def to_internal_value(self, data):
        data = {
            "wallet": data.get("wallet"),
            "amount": data.get("amount"),
        }
        return super().to_internal_value(data)

    def validate(self, attrs):
        """
        Extra rule:
        - user cannot create a new Charge if they already have a pending one
          on any of their wallets (or you can scope it to this wallet only).
        """
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return attrs

        wallet = attrs.get("wallet")
        if wallet.owner_id != request.user.id:
            raise serializers.ValidationError("You can only create charges on your own wallets.")

        has_pending = Charge.objects.filter(
            wallet__owner=request.user,
            status=TransactionStatuses.PENDING.value,
        ).exists()
        if has_pending:
            raise serializers.ValidationError("You already have a pending charge.")

        return attrs


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"


class TransferCreateSerializer(serializers.Serializer):
    source_wallet_id = serializers.IntegerField()
    target_phone = serializers.CharField()
    amount = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        source_id = attrs["source_wallet_id"]
        target_phone = attrs["target_phone"]
        amount = attrs["amount"]

        # get source wallet, lock will be in service
        try:
            source_wallet = Wallet.objects.get(id=source_id)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"source_wallet_id": "Source wallet not found"})

        # optional: ensure it's user's own wallet
        if user and source_wallet.owner_id != user.id:
            raise serializers.ValidationError({"source_wallet_id": "Not your wallet"})

        # find target wallet by phone (wallet.phone or wallet.owner.phone)
        try:
            target_wallet = Wallet.objects.get(phone_number=target_phone, is_active=True)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError({"target_phone": "Target wallet not found"})

        if source_wallet.id == target_wallet.id:
            raise serializers.ValidationError("Cannot transfer to same wallet")

        # attach resolved objects for view/service
        attrs["source_wallet"] = source_wallet
        attrs["target_wallet"] = target_wallet
        return attrs