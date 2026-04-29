from django import forms
from .models import Lesson, Group, Subject, Teacher, Classroom, TimeSlot, DAYS_OF_WEEK, WEEK_TYPES, SUBGROUP_TYPES, LANGUAGE_TYPES, CLASSROOM_TYPES


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['group', 'subject', 'teacher', 'classroom', 'day', 'time_slot',
                  'week_type', 'subgroup', 'lesson_type', 'language']
        widgets = {
            'group':       forms.Select(attrs={'class': 'form-select'}),
            'subject':     forms.Select(attrs={'class': 'form-select'}),
            'teacher':     forms.Select(attrs={'class': 'form-select'}),
            'classroom':   forms.Select(attrs={'class': 'form-select'}),
            'day':         forms.Select(attrs={'class': 'form-select'}),
            'time_slot':   forms.Select(attrs={'class': 'form-select'}),
            'week_type':   forms.Select(attrs={'class': 'form-select'}),
            'subgroup':    forms.Select(attrs={'class': 'form-select'}),
            'lesson_type': forms.Select(attrs={'class': 'form-select'}),
            'language':    forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        day       = cleaned.get('day')
        time_slot = cleaned.get('time_slot')
        week_type = cleaned.get('week_type')
        teacher   = cleaned.get('teacher')
        classroom = cleaned.get('classroom')
        group     = cleaned.get('group')
        subgroup  = cleaned.get('subgroup')
        lesson_type = cleaned.get('lesson_type')
        instance_id = self.instance.pk

        if not all([day, time_slot, week_type, teacher, classroom, group]):
            return cleaned

        # weeks that this lesson covers
        def overlaps(wt1, wt2):
            if wt1 == 'BOTH' or wt2 == 'BOTH':
                return True
            return wt1 == wt2

        base_qs = Lesson.objects.filter(day=day, time_slot=time_slot)
        if instance_id:
            base_qs = base_qs.exclude(pk=instance_id)

        # Teacher conflict
        for existing in base_qs.filter(teacher=teacher):
            if overlaps(week_type, existing.week_type):
                raise forms.ValidationError(
                    f"⚠️ Mugallym '{teacher}' bu wagty eýýäm başga bir sapakda: "
                    f"{existing.group} — {existing.subject} ({existing.get_week_type_display()})"
                )

        # Classroom conflict
        for existing in base_qs.filter(classroom=classroom):
            if overlaps(week_type, existing.week_type):
                raise forms.ValidationError(
                    f"⚠️ '{classroom}' otagy bu wagty eýýäm başga sapakda: "
                    f"{existing.group} — {existing.subject} ({existing.get_week_type_display()})"
                )

        # Group conflict (same subgroup or FULL)
        for existing in base_qs.filter(group=group):
            if overlaps(week_type, existing.week_type):
                sg1, sg2 = subgroup, existing.subgroup
                # FULL clashes with everything; SUB1 clashes with SUB1, etc.
                if sg1 == 'FULL' or sg2 == 'FULL' or sg1 == sg2:
                    raise forms.ValidationError(
                        f"⚠️ '{group}' topary ({subgroup}) bu wagty eýýäm başga sapakda: "
                        f"{existing.subject} — {existing.get_subgroup_display()} ({existing.get_week_type_display()})"
                    )

        # Lab must be in lab classroom
        if lesson_type == 'LAB' and classroom and classroom.classroom_type != 'LAB':
            raise forms.ValidationError(
                f"⚠️ Laboratoriýa sapagyny diňe laboratoriýa otagynda geçirip bolar. "
                f"'{classroom.name}' — {classroom.get_classroom_type_display()}"
            )

        # Lec should be in lec hall (warning only — not hard error, just validate)
        return cleaned
