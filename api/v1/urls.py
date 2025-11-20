from django.urls import path, include


urlpatterns = [
    path('auth/', include('apps.main.urls')),
    #path('students/', include('apps.students.urls')),
    #path('sponsors/', include('apps.sponsors.urls')),
   # path('bursaries/', include('apps.bursaries.urls')),
]
