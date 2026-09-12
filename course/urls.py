from django.urls import path
from . import views
from . import session_views
from . import payment_views
from . import test_booking_views
from . import reschedule_views
from .views import WeeklyScheduleView

app_name = 'course'

urlpatterns = [
    path('course_list/', views.CourseListView.as_view(), name='course_list'),
    path('my_courses/', views.MyCourseListView.as_view(), name='my_courses'),
    path('course_create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course_detail/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),

    path('<int:pk>/schedule/', WeeklyScheduleView.as_view(), name='weekly_schedule'),
    path('<int:pk>/timeslot/add/', views.TimeSlotCreateView.as_view(), name='timeslot_add'),
    path('courses/<int:pk>/timeslots/generate/', views.generate_more_timeslots, name='generate_more_timeslots'),

    path('timeslot/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('cart/success/', views.cart_payment_success, name='cart_payment_success'),
    path('cart/cancel/', views.cart_payment_cancel, name='cart_payment_cancel'),

    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('teacher_bookings/', views.teacher_bookings, name='teacher_bookings'),
    path('manager/test-tutoring-booking/', test_booking_views.create_test_tutoring_booking, name='create_test_tutoring_booking'),

    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:pk>/reschedule/', reschedule_views.request_reschedule, name='request_reschedule'),
    path('booking/<int:pk>/reschedule/cancel-after-decline/', reschedule_views.cancel_after_declined_reschedule, name='cancel_after_declined_reschedule'),
    path('booking/<int:pk>/reschedule/<str:decision>/', reschedule_views.respond_reschedule, name='respond_reschedule'),
    path('booking/<int:pk>/session/', session_views.tutoring_session, name='tutoring_session'),
    path('booking/<int:pk>/session/join/', session_views.session_join, name='session_join'),
    path('booking/<int:pk>/session/heartbeat/', session_views.session_heartbeat, name='session_heartbeat'),
    path('booking/<int:pk>/session/leave/', session_views.session_leave, name='session_leave'),
    path('booking/<int:pk>/session/review/', session_views.review_tutoring_session, name='review_tutoring_session'),
    path('booking/<int:pk>/session/report/', session_views.report_session_issue, name='report_session_issue'),

    path("set-timezone/", views.set_student_timezone, name="set_student_timezone"),

    path("stripe/connect/", views.stripe_connect_onboard, name="stripe_connect_onboard"),
    path("stripe/connect/refresh/", views.stripe_connect_refresh, name="stripe_connect_refresh"),
    path("stripe/connect/return/", views.stripe_connect_return, name="stripe_connect_return"),
    path("stripe/webhook/", payment_views.stripe_webhook, name="stripe_webhook"),
]
