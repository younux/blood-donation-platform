from rest_framework.generics import (
        CreateAPIView,
        GenericAPIView,
        )
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    )
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_200_OK,
        HTTP_400_BAD_REQUEST,
        HTTP_201_CREATED,
        )
from django.db.models import Q
from django.contrib.sites.models import Site
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from ..models import Profile
from .tokens import (JWTTokenGenerator,
                    AccountActivationTokenGenerator,
                    CustomPasswordResetTokenGenerator)

from .serializers import (
    ProfileCreateSerialzer,
    ProfileLoginSerializer,
    ProfileActivateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetSerializer,
    )
from .emails import send_activation_email, send_password_reset_email

class ProfileCreateAPIView(GenericAPIView):
    """
        Profile Create API VIEW.

        Extends GenericAPIView and defines post method. It handles the creation process
    """
    serializer_class = ProfileCreateSerialzer

    def post(self, request, *args, **kwargs):
        """
            Post Method

            Implements Post method that saves profile in database
            and sends a registration activation email
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Calling .save() will either create a new instance, or update an existing instance, depending on if an
        # existing instance was passed when instantiating the serializer class:
        profile_obj = serializer.save()  # The created user is inactive : see create_profile of ProfileManager
        # Create uid and token that will be sent by mail
        account_activation_token = AccountActivationTokenGenerator()
        uidb64, token = account_activation_token.make_uidb64_and_token(profile_obj)
        # Get the current Site based on the SITE_ID in the project's settings.
        my_site = Site.objects.get_current()
        # Send activation email
        send_activation_email(profile_obj, uidb64, token, my_site.domain)
        return Response(data=serializer.data, status=HTTP_201_CREATED)


class ProfileLoginAPIView(GenericAPIView):
    """
        Profile Create API VIEW.

        Extends GenericAPIView and defines post method. It handles the login process
    """
    permission_classes = [AllowAny]
    serializer_class = ProfileLoginSerializer

    def post(self, request, *args, **kwargs):
        """
            Post Method

            Implements Post method and sends a generated token in the the response header
        """
        data = request.data
        serializer = self.get_serializer(data = data)
        serializer.is_valid(raise_exception=True)
        # update last login and Generate Token
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        profile_obj = Profile.objects.all_active().filter(
                        Q(username=username) |
                        Q(email=email)
                    ).distinct().exclude(email__isnull=True).exclude(email__iexact='').first()
        # update last login date
        profile_obj.update_last_login()
        # Generate Token and add it to response header
        token = JWTTokenGenerator.generate_token(user = profile_obj)
        headers = {}
        headers['Authorization'] = JWTTokenGenerator.JWT_AUTH_HEADER_PREFIX + " " + token
        # By default Response status is 200, so we can omit status=HTTP_200_OK
        return Response(data=serializer.data, headers=headers)



class ProfileActivateAPIView(GenericAPIView):
    """
        Profile activate API VIEW.

        Extends GenericAPIView and defines post method. It handles the profile activation process.
    """

    permission_classes = [AllowAny]
    serializer_class = ProfileActivateSerializer

    def post(self, request, *args, **kwargs):
        """
            Post Method

            Implements Post method that checks the validity of the token using serializer
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        # Chekcs the validity of the serializer that checks the token
        serializer.is_valid(raise_exception=True)
        # Activate the profile
        uidb64 = serializer.validated_data.get('key')
        uid =  force_text(urlsafe_base64_decode(uidb64))
        profile_obj = Profile.objects.get(pk=uid)
        profile_obj.activate_profile()
        # By default Response status is 200, so we can omit status=HTTP_200_OK
        return Response(data=serializer.data)

class PasswordResetRequestAPIView(GenericAPIView):
    """
        Profile password reset request API VIEW.

        Extends GenericAPIView. This view handles receiving password reset request
         and sends a rest password email to the profile.
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        """
            Post Method

           Handles receiving password reset request and sends a rest password email to the profile.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        # Chekcs the validity of the serializer.
        serializer.is_valid(raise_exception=True)
        # Retrieve the concerned profile
        email = serializer.validated_data.get('email')
        profile_obj = Profile.objects.get(email=email)
        # Create uid and token that will be sent by mail
        password_reset_token = CustomPasswordResetTokenGenerator()
        uidb64, token = password_reset_token.make_uidb64_and_token(profile_obj)
        # Get the current Site based on the SITE_ID in the project's settings.
        my_site = Site.objects.get_current()
        # send email
        send_password_reset_email(profile_obj, uidb64, token, my_site.domain)
        # By default Response status is 200, so we can omit status=HTTP_200_OK
        return Response(data=serializer.data)

class PasswordResetVerifyAPIView(GenericAPIView):
    """
        Profile password reset verification API VIEW.

        Extends GenericAPIView.
        This view handles the verification of the token before requesting a new password.
        This can be used by the client to decide whether to show password redefinition form or not
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetVerifySerializer

    def post(self, request, *args, **kwargs):
        """
            Post Method

           Handles receiving password reset request and sends a rest password email to the profile.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        # Chekcs the validity of the serializer.
        serializer.is_valid(raise_exception=True)
        # By default Response status is 200, so we can omit status=HTTP_200_OK
        return Response(data=serializer.data)

class PasswordResetAPIView(GenericAPIView):
    """
        Final Profile password reset API VIEW.

        Extends GenericAPIView.
        This view handles the changing of the password
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        """
            Post Method

            Handles receiving password reset request and sends a rest password email to the profile.
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        # Chekcs the validity of the serializer.
        serializer.is_valid(raise_exception=True)
        # Redefine the profile password
        uidb64 = serializer.validated_data.get('key')
        password = serializer.validated_data.get('password')
        uid =  force_text(urlsafe_base64_decode(uidb64))
        profile_obj = Profile.objects.get(pk=uid)
        profile_obj.set_password(password)
        profile_obj.save()
        # By default Response status is 200, so we can omit status=HTTP_200_OK
        return Response(data=serializer.data)