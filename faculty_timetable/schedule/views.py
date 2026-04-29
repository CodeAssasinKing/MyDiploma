import json
from django.shortcuts import render, get_object_or_404
from .models import Group, Lesson, TimeSlot, Department, Classroom, Teacher, Subject
from django.shortcuts import redirect
DAYS_ORDER = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
DAYS_NAMES = {
    'MON': 'Dushenbe',
    'TUE': 'Sishenbe',
    'WED': 'Charshenbe',
    'THU': 'Penshenbe',
    'FRI': 'Anna',
    'SAT': 'Shenbe',
    'SUN': 'Yekshembe',
}


def dashboard(request):
    context = {
        'groups_count': Group.objects.count(),
        'teachers_count': Teacher.objects.count(),
        'classrooms_count': Classroom.objects.count(),
        'subjects_count': Subject.objects.count(),
        'lessons_count': Lesson.objects.count(),
        'departments': Department.objects.all(),
        'groups': Group.objects.all().order_by('course', 'name')[:10],
        'teachers': Teacher.objects.all(),
    }
    return render(request, 'schedule/dashboard.html', context)


def timetable_view(request):
    week_type = request.GET.get('week_type', 'ODD')
    department_id = request.GET.get('department', '')
    course = request.GET.get('course', '')

    groups = Group.objects.all().order_by('course', 'name').select_related('department')
    if department_id:
        groups = groups.filter(department_id=department_id)
    if course:
        groups = groups.filter(course=course)

    time_slots = TimeSlot.objects.all().order_by('number')
    departments = Department.objects.all()

    # Pre-fetch all relevant lessons
    lesson_qs = Lesson.objects.filter(
        week_type__in=[week_type, 'BOTH']
    ).select_related('subject', 'teacher', 'classroom', 'time_slot')

    if department_id:
        lesson_qs = lesson_qs.filter(group__department_id=department_id)
    if course:
        lesson_qs = lesson_qs.filter(group__course=course)

    # Build lookup: (day, timeslot_id, group_id) -> [lessons]
    lesson_map = {}
    for lesson in lesson_qs:
        key = (lesson.day, lesson.time_slot_id, lesson.group_id)
        if key not in lesson_map:
            lesson_map[key] = []
        lesson_map[key].append(lesson)

    # Build structured data for template
    timetable_rows = []
    for day_code in DAYS_ORDER:
        day_name = DAYS_NAMES[day_code]
        rows = []
        for ts in time_slots:
            cells = []
            for group in groups:
                key = (day_code, ts.id, group.id)
                cells.append({'group': group, 'lessons': lesson_map.get(key, [])})
            rows.append({'timeslot': ts, 'cells': cells})
        timetable_rows.append({'day_code': day_code, 'day_name': day_name, 'rows': rows})

    context = {
        'groups': groups,
        'time_slots': time_slots,
        'timetable_rows': timetable_rows,
        'week_type': week_type,
        'departments': departments,
        'selected_department': department_id,
        'selected_course': course,
        'courses': range(1, 6),
    }
    return render(request, 'schedule/timetable.html', context)


def teacher_list(request):
    teachers = Teacher.objects.all().select_related('department')
    context = {'teachers': teachers}
    return render(request, 'schedule/teacher_list.html', context)


def teacher_timetable(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    week_type = request.GET.get('week_type', 'ODD')
    time_slots = TimeSlot.objects.all().order_by('number')

    lesson_qs = Lesson.objects.filter(
        teacher=teacher,
        week_type__in=[week_type, 'BOTH']
    ).select_related('subject', 'group', 'classroom', 'time_slot')

    lesson_map = {}
    for lesson in lesson_qs:
        key = (lesson.day, lesson.time_slot_id)
        if key not in lesson_map:
            lesson_map[key] = []
        lesson_map[key].append(lesson)

    timetable_rows = []
    for day_code in DAYS_ORDER:
        rows = []
        for ts in time_slots:
            key = (day_code, ts.id)
            rows.append({'timeslot': ts, 'lessons': lesson_map.get(key, [])})
        timetable_rows.append({'day_code': day_code, 'day_name': DAYS_NAMES[day_code], 'rows': rows})

    context = {
        'teacher': teacher,
        'teachers': Teacher.objects.all().order_by('last_name'),
        'time_slots': time_slots,
        'timetable_rows': timetable_rows,
        'week_type': week_type,
    }
    return render(request, 'schedule/teacher_timetable.html', context)


def classroom_list(request):
    classrooms = Classroom.objects.all()
    context = {'classrooms': classrooms}
    return render(request, 'schedule/classroom_list.html', context)


def classroom_timetable(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    week_type = request.GET.get('week_type', 'ODD')
    time_slots = TimeSlot.objects.all().order_by('number')

    lesson_qs = Lesson.objects.filter(
        classroom=classroom,
        week_type__in=[week_type, 'BOTH']
    ).select_related('subject', 'group', 'teacher', 'time_slot')

    lesson_map = {}
    for lesson in lesson_qs:
        key = (lesson.day, lesson.time_slot_id)
        if key not in lesson_map:
            lesson_map[key] = []
        lesson_map[key].append(lesson)

    timetable_rows = []
    for day_code in DAYS_ORDER:
        rows = []
        for ts in time_slots:
            key = (day_code, ts.id)
            rows.append({'timeslot': ts, 'lessons': lesson_map.get(key, [])})
        timetable_rows.append({'day_code': day_code, 'day_name': DAYS_NAMES[day_code], 'rows': rows})

    context = {
        'classroom': classroom,
        'classrooms': Classroom.objects.all(),
        'time_slots': time_slots,
        'timetable_rows': timetable_rows,
        'week_type': week_type,
    }
    return render(request, 'schedule/classroom_timetable.html', context)


def group_timetable(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    week_type = request.GET.get('week_type', 'ODD')
    time_slots = TimeSlot.objects.all().order_by('number')

    lesson_qs = Lesson.objects.filter(
        group=group,
        week_type__in=[week_type, 'BOTH']
    ).select_related('subject', 'teacher', 'classroom', 'time_slot')

    lesson_map = {}
    for lesson in lesson_qs:
        key = (lesson.day, lesson.time_slot_id)
        if key not in lesson_map:
            lesson_map[key] = []
        lesson_map[key].append(lesson)

    timetable_rows = []
    for day_code in DAYS_ORDER:
        rows = []
        for ts in time_slots:
            key = (day_code, ts.id)
            rows.append({'timeslot': ts, 'lessons': lesson_map.get(key, [])})
        timetable_rows.append({'day_code': day_code, 'day_name': DAYS_NAMES[day_code], 'rows': rows})

    context = {
        'group': group,
        'groups': Group.objects.all().order_by('course', 'name'),
        'time_slots': time_slots,
        'timetable_rows': timetable_rows,
        'week_type': week_type,
    }
    return render(request, 'schedule/group_timetable.html', context)


# ─── LESSON CRUD ───────────────────────────────────────────────

from django.http import JsonResponse
from .forms import LessonForm


def lesson_create(request):
    """Create a new lesson."""
    group_id     = request.GET.get('group', '')
    day          = request.GET.get('day', '')
    slot_id      = request.GET.get('slot', '')
    teacher_id   = request.GET.get('teacher', '')
    classroom_id = request.GET.get('classroom', '')

    initial = {}
    if group_id:     initial['group']     = group_id
    if day:          initial['day']       = day
    if slot_id:      initial['time_slot'] = slot_id
    if teacher_id:   initial['teacher']   = teacher_id
    if classroom_id: initial['classroom'] = classroom_id

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            from django.shortcuts import redirect
            next_url = request.POST.get('next', '') or request.GET.get('next', '')
            return redirect(next_url if next_url else 'timetable')
    else:
        form = LessonForm(initial=initial)

    # For smart dropdowns
    groups     = Group.objects.all().order_by('course', 'name').select_related('department')
    subjects   = Subject.objects.all().order_by('name').select_related('department')
    teachers   = Teacher.objects.all().order_by('last_name').select_related('department')
    classrooms = Classroom.objects.all().order_by('name')
    time_slots = TimeSlot.objects.all().order_by('number')

    from .models import DAYS_OF_WEEK, WEEK_TYPES, SUBGROUP_TYPES, LANGUAGE_TYPES, CLASSROOM_TYPES
    context = {
        'form': form,
        'groups': groups,
        'subjects': subjects,
        'teachers': teachers,
        'classrooms': classrooms,
        'time_slots': time_slots,
        'days': DAYS_OF_WEEK,
        'week_types': WEEK_TYPES,
        'subgroups': SUBGROUP_TYPES,
        'languages': LANGUAGE_TYPES,
        'lesson_types': CLASSROOM_TYPES,
        'edit_mode': False,
        'next_url': request.GET.get('next', '') or request.POST.get('next', ''),
    }
    from django.shortcuts import render
    return render(request, 'schedule/lesson_form.html', context)


def lesson_edit(request, lesson_id):
    """Edit an existing lesson."""
    from django.shortcuts import get_object_or_404, redirect
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            next_url = request.POST.get('next', '')
            return redirect(next_url if next_url else 'timetable')
    else:
        form = LessonForm(instance=lesson)

    groups     = Group.objects.all().order_by('course', 'name').select_related('department')
    subjects   = Subject.objects.all().order_by('name').select_related('department')
    teachers   = Teacher.objects.all().order_by('last_name').select_related('department')
    classrooms = Classroom.objects.all().order_by('name')
    time_slots = TimeSlot.objects.all().order_by('number')

    from .models import DAYS_OF_WEEK, WEEK_TYPES, SUBGROUP_TYPES, LANGUAGE_TYPES, CLASSROOM_TYPES
    context = {
        'form': form,
        'lesson': lesson,
        'groups': groups,
        'subjects': subjects,
        'teachers': teachers,
        'classrooms': classrooms,
        'time_slots': time_slots,
        'days': DAYS_OF_WEEK,
        'week_types': WEEK_TYPES,
        'subgroups': SUBGROUP_TYPES,
        'languages': LANGUAGE_TYPES,
        'lesson_types': CLASSROOM_TYPES,
        'edit_mode': True,
        'next_url': request.GET.get('next', '') or request.POST.get('next', ''),
    }
    from django.shortcuts import render
    return render(request, 'schedule/lesson_form.html', context)


def lesson_delete(request, lesson_id):
    from django.shortcuts import get_object_or_404, redirect
    lesson = get_object_or_404(Lesson, id=lesson_id)
    next_url = request.POST.get('next', '') or request.GET.get('next', '')
    if request.method == 'POST':
        lesson.delete()
        return redirect(next_url if next_url else 'timetable')
    context = {'lesson': lesson, 'next': next_url}
    from django.shortcuts import render
    return render(request, 'schedule/lesson_confirm_delete.html', context)


def api_subjects_for_type(request):
    """Return subjects filtered by lesson_type for smart dropdown."""
    lesson_type = request.GET.get('type', '')
    subjects = Subject.objects.all()
    if lesson_type:
        subjects = subjects.filter(subject_type=lesson_type)
    data = [{'id': s.id, 'name': s.name, 'short': s.short_name} for s in subjects]
    return JsonResponse({'subjects': data})


def api_classrooms_for_type(request):
    """Return classrooms filtered by type."""
    lesson_type = request.GET.get('type', '')
    classrooms = Classroom.objects.all()
    if lesson_type == 'LAB':
        classrooms = classrooms.filter(classroom_type='LAB')
    elif lesson_type == 'LEC':
        classrooms = classrooms.filter(classroom_type='LEC')
    data = [{'id': c.id, 'name': c.name, 'type': c.classroom_type, 'cap': c.capacity} for c in classrooms]
    return JsonResponse({'classrooms': data})


def api_teachers_for_group(request):
    """Return teachers, flagging english-capable ones."""
    group_id = request.GET.get('group', '')
    teachers = Teacher.objects.all().order_by('last_name')
    if group_id:
        try:
            group = Group.objects.get(pk=group_id)
            if group.group_type == 'EN':
                teachers = teachers.filter(can_teach_english=True)
        except Group.DoesNotExist:
            pass
    data = [{'id': t.id, 'name': str(t), 'eng': t.can_teach_english} for t in teachers]
    return JsonResponse({'teachers': data})


def lesson_list(request):
    """Full lesson management list with filters."""
    lessons = Lesson.objects.all().select_related(
        'subject', 'teacher', 'group', 'classroom', 'time_slot'
    ).order_by('day', 'time_slot__number', 'group__name')

    # Filters
    group_id    = request.GET.get('group', '')
    teacher_id  = request.GET.get('teacher', '')
    day         = request.GET.get('day', '')
    week_type   = request.GET.get('week_type', '')
    lesson_type = request.GET.get('lesson_type', '')

    if group_id:    lessons = lessons.filter(group_id=group_id)
    if teacher_id:  lessons = lessons.filter(teacher_id=teacher_id)
    if day:         lessons = lessons.filter(day=day)
    if week_type:   lessons = lessons.filter(week_type=week_type)
    if lesson_type: lessons = lessons.filter(lesson_type=lesson_type)

    from .models import DAYS_OF_WEEK, WEEK_TYPES, CLASSROOM_TYPES
    context = {
        'lessons':      lessons,
        'groups':       Group.objects.all().order_by('course', 'name'),
        'teachers':     Teacher.objects.all().order_by('last_name'),
        'days':         DAYS_OF_WEEK,
        'week_types':   WEEK_TYPES,
        'lesson_types': CLASSROOM_TYPES,
        'f_group':      group_id,
        'f_teacher':    teacher_id,
        'f_day':        day,
        'f_week_type':  week_type,
        'f_lesson_type':lesson_type,
        'total':        lessons.count(),
    }
    from django.shortcuts import render
    return render(request, 'schedule/lesson_list.html', context)


# ─── AUTO-GENERATOR VIEWS ───────────────────────────────────────

from .generator import TimetableGenerator, GeneratorError
from .models import Curriculum


def generator_view(request):
    """Main timetable generator configuration page."""
    groups   = Group.objects.all().order_by('course', 'name').select_related('department')
    departments = Department.objects.all()

    # Curriculum summary per group — list of (group, [curricula])
    raw_map = {}
    for cur in Curriculum.objects.select_related('group', 'subject', 'preferred_teacher').order_by('group__name', 'lesson_type'):
        raw_map.setdefault(cur.group_id, []).append(cur)
    curriculum_map = raw_map   # kept for backward compat
    # Build list for template: [(group, [cur, ...]), ...]
    group_curriculum_list = []
    for g in (Group.objects.filter(pk__in=group_ids).order_by('course','name') if False else
              Group.objects.all().order_by('course','name')):
        items = raw_map.get(g.pk, [])
        group_curriculum_list.append((g, items))

    # Stats
    stats = {
        'groups':     groups.count(),
        'curriculum': Curriculum.objects.count(),
        'teachers':   Teacher.objects.count(),
        'classrooms': {'LAB': 0, 'LEC': 0, 'SIM': 0},
        'slots':      TimeSlot.objects.count(),
    }
    from django.db.models import Count
    for row in Classroom.objects.values('classroom_type').annotate(n=Count('id')):
        stats['classrooms'][row['classroom_type']] = row['n']

    from .models import DAYS_OF_WEEK
    days_list = DAYS_OF_WEEK
    days_json_val = [[d[0], d[1]] for d in days_list]

    context = {
        'groups': groups,
        'departments': departments,
        'curriculum_map': curriculum_map,
        'stats': stats,
        'lesson_count': Lesson.objects.count(),
        'group_curriculum_list': group_curriculum_list,
        'days_list': days_list,
        'days_json': json.dumps(days_json_val),
        'daily_opts': [2, 3, 4, 5, 6],
    }
    return render(request, 'schedule/generator.html', context)


def generator_run(request):
    """POST — run the generator and show results."""
    if request.method != 'POST':
        from django.shortcuts import redirect
        return redirect('generator')

    # Parse options from form
    group_ids_raw    = request.POST.getlist('group_ids')
    clear_existing   = request.POST.get('clear_existing') == 'on'
    max_daily        = int(request.POST.get('max_daily', 4))
    days_raw         = request.POST.getlist('preferred_days')
    preferred_days   = days_raw if days_raw else ['MON','TUE','WED','THU','FRI','SAT']

    group_ids = [int(g) for g in group_ids_raw] if group_ids_raw else None

    try:
        gen = TimetableGenerator(
            group_ids=group_ids,
            clear_existing=clear_existing,
            max_daily_lessons=max_daily,
            preferred_days=preferred_days,
        )
        created_count, skipped, warnings = gen.run()

        context = {
            'success': True,
            'created_count': created_count,
            'skipped': skipped,
            'warnings': warnings,
            'lesson_count': Lesson.objects.count(),
            'groups': Group.objects.filter(pk__in=group_ids) if group_ids else Group.objects.all(),
        }
    except GeneratorError as e:
        context = {
            'success': False,
            'error': str(e),
        }

    return render(request, 'schedule/generator_result.html', context)


def curriculum_view(request):
    """Manage curriculum (what each group needs to study)."""
    groups = Group.objects.all().order_by('course', 'name').select_related('department')
    selected_group_id = request.GET.get('group', '')

    curricula = Curriculum.objects.select_related(
        'group', 'subject', 'preferred_teacher'
    ).order_by('group__course', 'group__name', 'lesson_type')

    if selected_group_id:
        curricula = curricula.filter(group_id=selected_group_id)

    subjects  = Subject.objects.all().order_by('name')
    teachers  = Teacher.objects.all().order_by('last_name')

    from .models import CLASSROOM_TYPES
    context = {
        'curricula': curricula,
        'groups': groups,
        'subjects': subjects,
        'teachers': teachers,
        'lesson_types': CLASSROOM_TYPES,
        'selected_group_id': selected_group_id,
        'total': curricula.count(),
    }
    return render(request, 'schedule/curriculum.html', context)


def curriculum_add(request):
    """Add a curriculum item."""
    if request.method == 'POST':
        from django.shortcuts import redirect
        try:
            Curriculum.objects.update_or_create(
                group_id   = int(request.POST['group']),
                subject_id = int(request.POST['subject']),
                lesson_type= request.POST['lesson_type'],
                defaults={
                    'hours_per_week':    int(request.POST.get('hours_per_week', 1)),
                    'preferred_teacher': Teacher.objects.filter(
                        pk=request.POST.get('preferred_teacher')
                    ).first() if request.POST.get('preferred_teacher') else None,
                }
            )
        except Exception as e:
            pass
        next_url = request.POST.get('next', '') or request.GET.get('next', '')
        return redirect(next_url if next_url else 'curriculum')
    from django.shortcuts import redirect
    return redirect('curriculum')


def curriculum_delete(request, pk):
    """Delete a curriculum item."""
    from django.shortcuts import get_object_or_404, redirect
    cur = get_object_or_404(Curriculum, pk=pk)
    next_url = request.POST.get('next', '') or request.GET.get('next', '')
    if request.method == 'POST':
        cur.delete()
    return redirect(next_url if next_url else 'curriculum')




def delete_all_lessons(request):
    if request.method == "POST":
        lessons = Lesson.objects.all()
        lessons.delete()
        return redirect("dashboard")
