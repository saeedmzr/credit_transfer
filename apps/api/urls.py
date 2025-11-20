from django.urls import path, include

urlpatterns = [
    path('users/', include(('apps.users.urls', 'users'))),
    path('billing/', include(('apps.billing.urls', 'billing'))),
]
