from django.urls import path, include

from accounts.views import (
    CustomTokenObtainView, 
    CustomTokenRefreshView, 
    CustomTokenVerifyView
)

from .auth import (
    PasswordResetRequestView,
    PasswordResetVerifyView,
    ResendOTPView,
    UserRegisterView,
    VerifyOTPView,
)

from .endpoint import (
    # expert
    GetExpertProfile,
    UpdateExpertProfile,
    UploadExpertProfilePhoto,
    FetchExpertFilter,

    TopExpertsAPIView
)


# url patterns for auth
AUTH_URLPATTERNS = [
    path('jwt/create', CustomTokenObtainView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify', CustomTokenVerifyView.as_view(), name='token_verify'),
]

USER_URLPATTERNS = [
    # path("approve-skilled-user/<int:pk>/", ApproveSkilledUserView.as_view(), name="approve-skilled-user"),
    path("register", UserRegisterView.as_view(), name="register"),
    path("password_reset/request", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password_reset/verify", PasswordResetVerifyView.as_view(), name="password-reset-verify"),
    path("resend_otp", ResendOTPView.as_view(), name="resend_otp"),
    path("verify_otp", VerifyOTPView.as_view(), name="verify_otp"),

    


    # expert
    path("get_expert", GetExpertProfile.as_view(), name="get_expert"),
    path('update_expert_profile', UpdateExpertProfile.as_view(), name='expert-profile'),
    path('update_expert_photo', UploadExpertProfilePhoto.as_view(), name='profile-photo'),
    path('top_experts', TopExpertsAPIView.as_view(), name='top_experts'),
    path('fetch_experts', FetchExpertFilter.as_view(), name='fetch_experts'),
]

urlpatterns = AUTH_URLPATTERNS + USER_URLPATTERNS 

