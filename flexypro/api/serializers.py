from audioop import reverse
from rest_framework import serializers

from api.utils import Util
from .models import (
    Order, 
    Client, 
    Notification, 
    Rating, 
    Solved,
    Chat, 
    Transaction,
    Solution,
    Profile,
    Freelancer,
    User,
    OTP,

)
# from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q

class setNewPasswordSerializer(serializers.ModelSerializer):
    password_1 = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
    )
    password_2 = serializers.CharField(
        write_only=True, 
        required=True, 
    )
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model=User
        fields = ['password_1','password_2','token','uidb64']
    
    def validate(self, attrs):
        # try:
        password = attrs.get('password_1')
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')

        if attrs.get('password_1') != attrs.get('password_2'):
            print("Passwords did not match")
            raise serializers.ValidationError({
                'password_error':["Passwords did not match"]
            })

        id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed({
                'error':['Reset link used']
            }, 401)
        
        user.set_password(password)
        user.save()
            
        return super().validate(attrs)

class ResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=2)
    class Meta:
        fields=['email']    

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields=['otp','used']
        ordering = ['--timestamp']

class ObtainTokenSerializerClient(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        try:            
            Client.objects.get(user=user)
        except:
            raise serializers.ValidationError("No such client found. Authentication Failed", code='authentication')
        
        token= super(ObtainTokenSerializerClient, cls).get_token(user)
        token['username'] = user.username
        return token  

class ObtainTokenSerializerFreelancer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        try:            
            Freelancer.objects.get(user=user)
        except:
            raise serializers.ValidationError("You're not registered. Authentication Failed", code='authentication')
        
        token= super(ObtainTokenSerializerFreelancer, cls).get_token(user)
        token['username'] = user.username
        return token 
    
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(        
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message = [            
            'This email address is already in use'           
        ])],        
    )
    password_1 = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
    )
    password_2 = serializers.CharField(
        write_only=True, 
        required=True
    )

    class Meta:
        model=User
        fields = (
            'username','password_1','password_2','email','first_name','last_name'
        )
    
    def validate(self, attrs):
        if attrs['password_1'] != attrs['password_2']:
            raise serializers.ValidationError({
                'password_error':"Passwords did not match"
            })
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password_1'])
        user.save()
        Client.objects.create(
            user=user
        )
        return user

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
        ]

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(serializers.ModelSerializer)
    
    class Meta:
        model = Client
        exclude = ['id']

class FreelancerSerializer(serializers.ModelSerializer):
    user = UserSerializer(serializers.ModelSerializer)
    
    class Meta:
        model = Freelancer
        exclude = ['id']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            'rating'
        ]

class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = [
            'solution', '_type','created'
        ]  

class OrderSerializer(serializers.ModelSerializer): 
    client = ClientSerializer(read_only=True)
    freelancer = FreelancerSerializer(read_only=True)
    solution = SolutionSerializer(read_only=True)
    rating = RatingSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
    
    # def get_solution(self,obj):
    #     return obj.solution

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    order_id = serializers.CharField(source='order.id', read_only=True)    

    class Meta:
        model = Notification
        fields = ['id','user','message', 'order_id', 'read_status', 'created_at']
        ordering = ['-created_at']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    orders_count = serializers.SerializerMethodField()
    is_verified = serializers.CharField(source='user.is_verified', read_only=True)

    # notification_count = serializers.SerializerMethodField()
    # unread_notifications = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'username', 
            'email',
            'first_name', 
            'last_name', 
            'is_verified',
            'orders_count',
            # 'notification_count', 
            # 'unread_notifications',
            'bio', 
            'profile_photo'
        ]
    # def get_verified_status(self, profile):
    #     user = profile.user
    #     is_verified = user.is_verified
    #     return is_verified
        
    # def get_notification_count(self, profile):
    #     user = profile.user        
    #     notification_count = Notification.objects.filter(user=user).count()
    #     return notification_count

    # def get_unread_notifications(self, profile):
    #     user = profile.user
    #     unread_notifications = Notification.objects.filter(user=user, read_status=False).count()
    #     return unread_notifications

    def get_orders_count(self, profile):
        user = profile.user
        query = Q(client__user=user) | Q(freelancer__user=user)

        orders_count = Order.objects.filter(query).count()
        return orders_count
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['last_login'] = instance.user.last_login
        return data

class SolvedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Solved
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = Chat
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    _from = ClientSerializer(read_only=True)
    to = UserSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'