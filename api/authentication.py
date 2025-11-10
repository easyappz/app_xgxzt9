from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Member


class MemberJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that uses Member model instead of Django User model.
    """
    def get_user(self, validated_token):
        try:
            member_id = validated_token.get('member_id')
            if member_id is None:
                raise InvalidToken('Token does not contain member_id')
            
            member = Member.objects.get(id=member_id)
            return member
        except Member.DoesNotExist:
            raise InvalidToken('Member not found')
