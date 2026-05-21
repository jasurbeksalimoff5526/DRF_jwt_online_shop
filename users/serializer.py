from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser, CodeVerify, VIA_EMAIL, VIA_PHONE
from shared.utility import check_email_or_phone


class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email_or_phone', 'auth_type', 'auth_status']
        read_only_fields = ['auth_type', 'auth_status']

    def validate_email_or_phone(self, value):
        value = value.strip().lower()

        field_type = check_email_or_phone(value)

        if field_type == 'email':
            if CustomUser.objects.filter(email=value).exists():
                raise ValidationError("Bu email allaqachon ro'yxatdan o'tgan!")

        elif field_type == 'phone':
            if CustomUser.objects.filter(phone_number=value).exists():
                raise ValidationError("Bu telefon raqami ro'yxatdan o'tgan!")

        else:
            raise ValidationError("Email yoki telefon noto'g'ri!")

        return value

    def create(self, validated_data):
        email_or_phone = validated_data.pop('email_or_phone')

        field_type = check_email_or_phone(email_or_phone)

        if field_type == 'email':
            validated_data['email'] = email_or_phone
            validated_data['auth_type'] = VIA_EMAIL

        else:
            validated_data['phone_number'] = email_or_phone
            validated_data['auth_type'] = VIA_PHONE

        user = CustomUser.objects.create(**validated_data)

        user.create_code(user.auth_type)

        return user

    def to_representation(self, instance):
        user = super().to_representation(instance)
        user['token'] = instance.token()
        return user