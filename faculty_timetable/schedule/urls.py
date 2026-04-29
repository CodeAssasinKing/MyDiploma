from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sapaklyk/', views.timetable_view, name='timetable'),
    path('sapaklyk/sanaw/', views.lesson_list, name='lesson_list'),
    path('mugallymlar/', views.teacher_list, name='teacher_list'),
    path('mugallymlar/<int:teacher_id>/', views.teacher_timetable, name='teacher_timetable'),
    path('otaglar/', views.classroom_list, name='classroom_list'),
    path('otaglar/<int:classroom_id>/', views.classroom_timetable, name='classroom_timetable'),
    path('toparlar/<int:group_id>/', views.group_timetable, name='group_timetable'),
    # Lesson CRUD
    path('sapak/gos/', views.lesson_create, name='lesson_create'),
    path('sapak/<int:lesson_id>/duzet/', views.lesson_edit, name='lesson_edit'),
    path('sapak/<int:lesson_id>/poz/', views.lesson_delete, name='lesson_delete'),
    path('sapak/delete/lessons/', views.delete_all_lessons, name="delete_all_lessons"),
    # Auto-generator
    path('generator/', views.generator_view, name='generator'),
    path('generator/ishlet/', views.generator_run, name='generator_run'),
    # Curriculum
    path('okuw-plany/', views.curriculum_view, name='curriculum'),
    path('okuw-plany/gos/', views.curriculum_add, name='curriculum_add'),
    path('okuw-plany/<int:pk>/poz/', views.curriculum_delete, name='curriculum_delete'),
    # Smart APIs
    path('api/dersler/', views.api_subjects_for_type, name='api_subjects'),
    path('api/otaglar/', views.api_classrooms_for_type, name='api_classrooms'),
    path('api/mugallymlar/', views.api_teachers_for_group, name='api_teachers'),
]
