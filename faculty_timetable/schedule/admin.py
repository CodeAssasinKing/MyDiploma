from django.contrib import admin
from .models import Department, Group, Classroom, Teacher, Subject, TimeSlot, Lesson

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'course', 'department', 'student_count']
    list_filter = ['group_type', 'course', 'department']

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'classroom_type', 'capacity', 'building']
    list_filter = ['classroom_type', 'building']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'position', 'can_teach_english', 'department']
    list_filter = ['department', 'can_teach_english']
    search_fields = ['last_name', 'first_name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject_type', 'department']
    list_filter = ['subject_type', 'department']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['number', 'start_time', 'end_time', 'shift']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['subject', 'group', 'teacher', 'classroom', 'day', 'time_slot', 'week_type', 'subgroup', 'lesson_type']
    list_filter = ['day', 'week_type', 'lesson_type', 'group__course', 'group__department']
    search_fields = ['subject__name', 'teacher__last_name', 'group__name']
    autocomplete_fields = []

from .models import Curriculum

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['group', 'subject', 'lesson_type', 'hours_per_week', 'preferred_teacher']
    list_filter  = ['lesson_type', 'group__course', 'group__department']
