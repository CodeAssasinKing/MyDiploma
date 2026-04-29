from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time
from schedule.models import (
    Department, Group, Classroom, Teacher, Subject,
    TimeSlot, Lesson
)


class Command(BaseCommand):
    help = 'Maglumat bazasyny nusga maglumatlar bilen dolduryar'

    def handle(self, *args, **kwargs):
        self.stdout.write('Nusga maglumatlary yuklenip baslandy...')

        # Clear
        Lesson.objects.all().delete()
        TimeSlot.objects.all().delete()
        Subject.objects.all().delete()
        Teacher.objects.all().delete()
        Classroom.objects.all().delete()
        Group.objects.all().delete()
        Department.objects.all().delete()

        # Departments
        dept = Department.objects.create(name='Informatika we Programmirleme', short_name='IP')
        dept2 = Department.objects.create(name='Matematika we Fizika', short_name='MF')

        # Time Slots - Pair lessons
        slots_data = [
            (1, time(8, 30), time(10, 0), 1),
            (2, time(10, 10), time(11, 40), 1),
            (3, time(11, 50), time(13, 20), 1),
            (4, time(14, 0), time(15, 30), 2),
            (5, time(15, 40), time(17, 10), 2),
            (6, time(17, 20), time(18, 50), 2),
        ]
        slots = {}
        for num, start, end, shift in slots_data:
            slots[num] = TimeSlot.objects.create(number=num, start_time=start, end_time=end, shift=shift)

        # Classrooms
        classrooms = {}
        classroom_data = [
            ('101', 'SIM', 30, 'A bina'),
            ('102', 'SIM', 30, 'A bina'),
            ('103', 'SIM', 25, 'A bina'),
            ('201', 'SIM', 30, 'A bina'),
            ('202', 'SIM', 30, 'A bina'),
            ('Leksiya-1', 'LEC', 120, 'B bina'),
            ('Leksiya-2', 'LEC', 100, 'B bina'),
            ('Lab-1', 'LAB', 20, 'B bina'),
            ('Lab-2', 'LAB', 20, 'B bina'),
            ('Lab-3', 'LAB', 20, 'C bina'),
        ]
        for name, ctype, cap, building in classroom_data:
            classrooms[name] = Classroom.objects.create(
                name=name, classroom_type=ctype, capacity=cap, building=building
            )

        # Groups
        group_data = [
            ('IP-21-A', 'EN', 3, dept, 25),
            ('IP-21-B', 'TM', 3, dept, 28),
            ('IP-22-A', 'EN', 2, dept, 24),
            ('IP-22-B', 'TM', 2, dept, 27),
            ('IP-23-A', 'TM', 1, dept, 30),
            ('IP-23-B', 'TM', 1, dept, 28),
            ('MF-22-A', 'TM', 2, dept2, 25),
            ('MF-23-A', 'TM', 1, dept2, 30),
        ]
        groups = {}
        for name, gtype, course, dep, count in group_data:
            groups[name] = Group.objects.create(
                name=name, group_type=gtype, course=course, department=dep, student_count=count
            )

        # Teachers
        teacher_data = [
            ('Meredow', 'Serdar', 'Amanowiç', True, dept, 'Dosent'),
            ('Hojayew', 'Batyr', 'Nurowiç', False, dept, 'Mugallym'),
            ('Annayewa', 'Oguljan', 'Halilowna', True, dept, 'Dosent'),
            ('Durdyyew', 'Maksat', 'Rejebowiç', False, dept, 'Mugallym'),
            ('Garryýew', 'Dawut', 'Orazowiç', False, dept, 'Professor'),
            ('Muhammedow', 'Azat', 'Baýramowiç', True, dept, 'Dosent'),
            ('Rahimowa', 'Leýla', 'Meredowna', False, dept2, 'Mugallym'),
            ('Baýramow', 'Yusup', 'Hydyrowiç', False, dept2, 'Dosent'),
        ]
        teachers = {}
        for last, first, patron, eng, dep, pos in teacher_data:
            teachers[last] = Teacher.objects.create(
                last_name=last, first_name=first, patronymic=patron,
                can_teach_english=eng, department=dep, position=pos
            )

        # Subjects
        subject_data = [
            ('Programmirleme esaslary', 'Prog. esaslary', 'LEC', dept),
            ('Programmirleme esaslary', 'Prog. lab', 'LAB', dept),
            ('Maglumat gurluslary we algoritmler', 'MGA', 'LEC', dept),
            ('Maglumat gurluslary we algoritmler', 'MGA lab', 'LAB', dept),
            ('Wep programmirleme', 'Wep prog.', 'SIM', dept),
            ('Maglumat bazalary', 'MB', 'SIM', dept),
            ('Operasion sistemalar', 'OS', 'LEC', dept),
            ('Kompyuter tory', 'Komp. tory', 'LAB', dept),
            ('Matematiki analiz', 'Mat. analiz', 'LEC', dept2),
            ('Fizika', 'Fizika', 'LEC', dept2),
        ]
        subjects = {}
        for name, short, stype, dep in subject_data:
            key = short
            subjects[key] = Subject.objects.create(
                name=name, short_name=short, subject_type=stype, department=dep
            )

        def add(subj_key, teacher_key, group_key, classroom_key, day, slot_num, week, subgroup, lang='TM'):
            lesson_type = subjects[subj_key].subject_type
            Lesson.objects.create(
                subject=subjects[subj_key],
                teacher=teachers[teacher_key],
                group=groups[group_key],
                classroom=classrooms[classroom_key],
                day=day,
                time_slot=slots[slot_num],
                week_type=week,
                subgroup=subgroup,
                lesson_type=lesson_type,
                language=lang,
            )

        # =====================
        # IP-21-A (English group, course 3)
        # =====================
        add('Prog. esaslary', 'Meredow', 'IP-21-A', 'Leksiya-1', 'MON', 1, 'BOTH', 'FULL', 'EN')
        add('Prog. lab', 'Annayewa', 'IP-21-A', 'Lab-1', 'MON', 2, 'ODD', 'SUB1', 'EN')
        add('Prog. lab', 'Annayewa', 'IP-21-A', 'Lab-2', 'MON', 2, 'ODD', 'SUB2', 'EN')
        add('Prog. lab', 'Meredow', 'IP-21-A', 'Lab-1', 'MON', 2, 'EVEN', 'SUB1', 'EN')
        add('Prog. lab', 'Meredow', 'IP-21-A', 'Lab-2', 'MON', 2, 'EVEN', 'SUB2', 'EN')
        add('MGA', 'Muhammedow', 'IP-21-A', 'Leksiya-2', 'TUE', 1, 'BOTH', 'FULL', 'EN')
        add('MGA lab', 'Muhammedow', 'IP-21-A', 'Lab-1', 'TUE', 2, 'ODD', 'SUB1', 'EN')
        add('MGA lab', 'Muhammedow', 'IP-21-A', 'Lab-2', 'TUE', 2, 'ODD', 'SUB2', 'EN')
        add('MGA lab', 'Annayewa', 'IP-21-A', 'Lab-1', 'TUE', 2, 'EVEN', 'SUB1', 'EN')
        add('MGA lab', 'Annayewa', 'IP-21-A', 'Lab-2', 'TUE', 2, 'EVEN', 'SUB2', 'EN')
        add('Wep prog.', 'Meredow', 'IP-21-A', '201', 'WED', 1, 'BOTH', 'FULL', 'EN')
        add('MB', 'Annayewa', 'IP-21-A', '202', 'WED', 2, 'BOTH', 'FULL', 'EN')
        add('OS', 'Garryýew', 'IP-21-A', 'Leksiya-1', 'THU', 1, 'BOTH', 'FULL', 'EN')
        add('Komp. tory', 'Muhammedow', 'IP-21-A', 'Lab-3', 'FRI', 1, 'ODD', 'SUB1', 'EN')
        add('Komp. tory', 'Muhammedow', 'IP-21-A', 'Lab-3', 'FRI', 2, 'ODD', 'SUB2', 'EN')
        add('Komp. tory', 'Meredow', 'IP-21-A', 'Lab-3', 'FRI', 1, 'EVEN', 'SUB1', 'EN')
        add('Komp. tory', 'Meredow', 'IP-21-A', 'Lab-3', 'FRI', 2, 'EVEN', 'SUB2', 'EN')

        # =====================
        # IP-21-B (Turkmen group, course 3)
        # =====================
        add('Prog. esaslary', 'Garryýew', 'IP-21-B', 'Leksiya-1', 'MON', 3, 'BOTH', 'FULL')
        add('Prog. lab', 'Hojayew', 'IP-21-B', 'Lab-1', 'TUE', 3, 'ODD', 'SUB1')
        add('Prog. lab', 'Hojayew', 'IP-21-B', 'Lab-2', 'TUE', 3, 'ODD', 'SUB2')
        add('Prog. lab', 'Durdyyew', 'IP-21-B', 'Lab-1', 'TUE', 3, 'EVEN', 'SUB1')
        add('Prog. lab', 'Durdyyew', 'IP-21-B', 'Lab-2', 'TUE', 3, 'EVEN', 'SUB2')
        add('MGA', 'Garryýew', 'IP-21-B', 'Leksiya-2', 'WED', 1, 'BOTH', 'FULL')
        add('MGA lab', 'Hojayew', 'IP-21-B', 'Lab-3', 'WED', 2, 'ODD', 'SUB1')
        add('MGA lab', 'Hojayew', 'IP-21-B', 'Lab-3', 'WED', 3, 'ODD', 'SUB2')
        add('MGA lab', 'Durdyyew', 'IP-21-B', 'Lab-3', 'WED', 2, 'EVEN', 'SUB1')
        add('MGA lab', 'Durdyyew', 'IP-21-B', 'Lab-3', 'WED', 3, 'EVEN', 'SUB2')
        add('Wep prog.', 'Hojayew', 'IP-21-B', '101', 'THU', 2, 'BOTH', 'FULL')
        add('MB', 'Durdyyew', 'IP-21-B', '102', 'THU', 3, 'BOTH', 'FULL')
        add('OS', 'Garryýew', 'IP-21-B', 'Leksiya-2', 'FRI', 1, 'BOTH', 'FULL')
        add('Komp. tory', 'Hojayew', 'IP-21-B', 'Lab-1', 'SAT', 1, 'ODD', 'SUB1')
        add('Komp. tory', 'Hojayew', 'IP-21-B', 'Lab-2', 'SAT', 2, 'ODD', 'SUB2')
        add('Komp. tory', 'Durdyyew', 'IP-21-B', 'Lab-1', 'SAT', 1, 'EVEN', 'SUB1')
        add('Komp. tory', 'Durdyyew', 'IP-21-B', 'Lab-2', 'SAT', 2, 'EVEN', 'SUB2')

        # =====================
        # IP-22-A (English group, course 2)
        # =====================
        add('Prog. esaslary', 'Meredow', 'IP-22-A', 'Leksiya-2', 'MON', 4, 'BOTH', 'FULL', 'EN')
        add('Prog. lab', 'Meredow', 'IP-22-A', 'Lab-1', 'MON', 5, 'ODD', 'SUB1', 'EN')
        add('Prog. lab', 'Meredow', 'IP-22-A', 'Lab-2', 'MON', 5, 'ODD', 'SUB2', 'EN')
        add('Prog. lab', 'Annayewa', 'IP-22-A', 'Lab-1', 'MON', 5, 'EVEN', 'SUB1', 'EN')
        add('Prog. lab', 'Annayewa', 'IP-22-A', 'Lab-2', 'MON', 5, 'EVEN', 'SUB2', 'EN')
        add('MGA', 'Annayewa', 'IP-22-A', 'Leksiya-1', 'TUE', 4, 'BOTH', 'FULL', 'EN')
        add('Wep prog.', 'Muhammedow', 'IP-22-A', '201', 'WED', 4, 'BOTH', 'FULL', 'EN')
        add('MB', 'Meredow', 'IP-22-A', '202', 'THU', 4, 'BOTH', 'FULL', 'EN')
        add('OS', 'Garryýew', 'IP-22-A', 'Leksiya-1', 'FRI', 4, 'BOTH', 'FULL', 'EN')
        add('Komp. tory', 'Muhammedow', 'IP-22-A', 'Lab-3', 'SAT', 4, 'ODD', 'SUB1', 'EN')
        add('Komp. tory', 'Muhammedow', 'IP-22-A', 'Lab-3', 'SAT', 5, 'ODD', 'SUB2', 'EN')
        add('Komp. tory', 'Annayewa', 'IP-22-A', 'Lab-3', 'SAT', 4, 'EVEN', 'SUB1', 'EN')
        add('Komp. tory', 'Annayewa', 'IP-22-A', 'Lab-3', 'SAT', 5, 'EVEN', 'SUB2', 'EN')

        # =====================
        # IP-22-B (Turkmen group, course 2)
        # =====================
        add('Prog. esaslary', 'Garryýew', 'IP-22-B', 'Leksiya-2', 'MON', 2, 'BOTH', 'FULL')
        add('MGA', 'Garryýew', 'IP-22-B', 'Leksiya-1', 'TUE', 2, 'BOTH', 'FULL')
        add('Prog. lab', 'Durdyyew', 'IP-22-B', 'Lab-1', 'TUE', 4, 'ODD', 'SUB1')
        add('Prog. lab', 'Durdyyew', 'IP-22-B', 'Lab-2', 'TUE', 4, 'ODD', 'SUB2')
        add('Prog. lab', 'Hojayew', 'IP-22-B', 'Lab-1', 'TUE', 4, 'EVEN', 'SUB1')
        add('Prog. lab', 'Hojayew', 'IP-22-B', 'Lab-2', 'TUE', 4, 'EVEN', 'SUB2')
        add('Wep prog.', 'Hojayew', 'IP-22-B', '103', 'WED', 4, 'BOTH', 'FULL')
        add('MB', 'Durdyyew', 'IP-22-B', '103', 'THU', 4, 'BOTH', 'FULL')
        add('OS', 'Garryýew', 'IP-22-B', 'Leksiya-2', 'FRI', 2, 'BOTH', 'FULL')
        add('MGA lab', 'Hojayew', 'IP-22-B', 'Lab-2', 'SAT', 1, 'ODD', 'SUB1')
        add('MGA lab', 'Hojayew', 'IP-22-B', 'Lab-3', 'SAT', 1, 'ODD', 'SUB2')
        add('MGA lab', 'Durdyyew', 'IP-22-B', 'Lab-2', 'SAT', 1, 'EVEN', 'SUB1')
        add('MGA lab', 'Durdyyew', 'IP-22-B', 'Lab-3', 'SAT', 1, 'EVEN', 'SUB2')

        # =====================
        # IP-23-A (Turkmen group, course 1)
        # =====================
        add('Prog. esaslary', 'Hojayew', 'IP-23-A', 'Leksiya-1', 'MON', 1, 'BOTH', 'FULL')
        add('Prog. lab', 'Hojayew', 'IP-23-A', 'Lab-1', 'MON', 2, 'ODD', 'SUB1')
        add('Prog. lab', 'Hojayew', 'IP-23-A', 'Lab-2', 'MON', 2, 'ODD', 'SUB2')
        add('Prog. lab', 'Durdyyew', 'IP-23-A', 'Lab-1', 'MON', 2, 'EVEN', 'SUB1')
        add('Prog. lab', 'Durdyyew', 'IP-23-A', 'Lab-2', 'MON', 2, 'EVEN', 'SUB2')
        add('Mat. analiz', 'Rahimowa', 'IP-23-A', 'Leksiya-2', 'TUE', 1, 'BOTH', 'FULL')
        add('Fizika', 'Baýramow', 'IP-23-A', 'Leksiya-1', 'WED', 1, 'BOTH', 'FULL')
        add('MGA', 'Garryýew', 'IP-23-A', 'Leksiya-2', 'THU', 1, 'BOTH', 'FULL')
        add('Wep prog.', 'Durdyyew', 'IP-23-A', '101', 'FRI', 1, 'BOTH', 'FULL')
        add('MB', 'Hojayew', 'IP-23-A', '102', 'SAT', 1, 'BOTH', 'FULL')

        # =====================
        # IP-23-B (Turkmen group, course 1)
        # =====================
        add('Prog. esaslary', 'Durdyyew', 'IP-23-B', 'Leksiya-1', 'MON', 3, 'BOTH', 'FULL')
        add('Mat. analiz', 'Baýramow', 'IP-23-B', 'Leksiya-2', 'TUE', 3, 'BOTH', 'FULL')
        add('Fizika', 'Rahimowa', 'IP-23-B', 'Leksiya-1', 'WED', 3, 'BOTH', 'FULL')
        add('MGA', 'Garryýew', 'IP-23-B', 'Leksiya-2', 'THU', 3, 'BOTH', 'FULL')
        add('Prog. lab', 'Durdyyew', 'IP-23-B', 'Lab-1', 'FRI', 2, 'ODD', 'SUB1')
        add('Prog. lab', 'Durdyyew', 'IP-23-B', 'Lab-2', 'FRI', 2, 'ODD', 'SUB2')
        add('Prog. lab', 'Hojayew', 'IP-23-B', 'Lab-1', 'FRI', 2, 'EVEN', 'SUB1')
        add('Prog. lab', 'Hojayew', 'IP-23-B', 'Lab-2', 'FRI', 2, 'EVEN', 'SUB2')
        add('Wep prog.', 'Hojayew', 'IP-23-B', '103', 'SAT', 2, 'BOTH', 'FULL')

        # =====================
        # MF-22-A and MF-23-A
        # =====================
        add('Mat. analiz', 'Rahimowa', 'MF-22-A', 'Leksiya-1', 'MON', 1, 'BOTH', 'FULL')
        add('Fizika', 'Baýramow', 'MF-22-A', 'Leksiya-2', 'TUE', 1, 'BOTH', 'FULL')
        add('Mat. analiz', 'Rahimowa', 'MF-23-A', 'Leksiya-2', 'MON', 2, 'BOTH', 'FULL')
        add('Fizika', 'Baýramow', 'MF-23-A', 'Leksiya-1', 'WED', 2, 'BOTH', 'FULL')

        self.stdout.write(self.style.SUCCESS(
            f'Tayyar! {Lesson.objects.count()} sapak, '
            f'{Group.objects.count()} topar, '
            f'{Teacher.objects.count()} mugallym yuklenildi.'
        ))

        # =====================
        # OKUW PLANY (Curriculum)
        # =====================
        from schedule.models import Curriculum
        Curriculum.objects.all().delete()

        def cur(group_name, subj_key, ltype, hours, teacher_name=None):
            g = groups[group_name]
            s = subjects[subj_key]
            t = teachers.get(teacher_name)
            Curriculum.objects.create(
                group=g, subject=s, lesson_type=ltype,
                hours_per_week=hours, preferred_teacher=t
            )

        # IP-21-A (English, course 3)
        cur('IP-21-A', 'Prog. esaslary', 'LEC', 1, 'Meredow')
        cur('IP-21-A', 'Prog. lab',      'LAB', 2, 'Annayewa')
        cur('IP-21-A', 'MGA',            'LEC', 1, 'Muhammedow')
        cur('IP-21-A', 'MGA lab',        'LAB', 2, 'Muhammedow')
        cur('IP-21-A', 'Wep prog.',      'SIM', 1, 'Meredow')
        cur('IP-21-A', 'MB',             'SIM', 1, 'Annayewa')
        cur('IP-21-A', 'OS',             'LEC', 1, 'Garryýew')
        cur('IP-21-A', 'Komp. tory',     'LAB', 2, 'Muhammedow')

        # IP-21-B (Turkmen, course 3)
        cur('IP-21-B', 'Prog. esaslary', 'LEC', 1, 'Garryýew')
        cur('IP-21-B', 'Prog. lab',      'LAB', 2, 'Hojayew')
        cur('IP-21-B', 'MGA',            'LEC', 1, 'Garryýew')
        cur('IP-21-B', 'MGA lab',        'LAB', 2, 'Hojayew')
        cur('IP-21-B', 'Wep prog.',      'SIM', 1, 'Hojayew')
        cur('IP-21-B', 'MB',             'SIM', 1, 'Durdyyew')
        cur('IP-21-B', 'OS',             'LEC', 1, 'Garryýew')
        cur('IP-21-B', 'Komp. tory',     'LAB', 2, 'Hojayew')

        # IP-22-A (English, course 2)
        cur('IP-22-A', 'Prog. esaslary', 'LEC', 1, 'Meredow')
        cur('IP-22-A', 'Prog. lab',      'LAB', 2, 'Meredow')
        cur('IP-22-A', 'MGA',            'LEC', 1, 'Annayewa')
        cur('IP-22-A', 'Wep prog.',      'SIM', 1, 'Muhammedow')
        cur('IP-22-A', 'MB',             'SIM', 1, 'Meredow')
        cur('IP-22-A', 'OS',             'LEC', 1, 'Garryýew')
        cur('IP-22-A', 'Komp. tory',     'LAB', 2, 'Muhammedow')

        # IP-22-B (Turkmen, course 2)
        cur('IP-22-B', 'Prog. esaslary', 'LEC', 1, 'Garryýew')
        cur('IP-22-B', 'Prog. lab',      'LAB', 2, 'Durdyyew')
        cur('IP-22-B', 'MGA',            'LEC', 1, 'Garryýew')
        cur('IP-22-B', 'MGA lab',        'LAB', 2, 'Hojayew')
        cur('IP-22-B', 'Wep prog.',      'SIM', 1, 'Hojayew')
        cur('IP-22-B', 'MB',             'SIM', 1, 'Durdyyew')
        cur('IP-22-B', 'OS',             'LEC', 1, 'Garryýew')

        # IP-23-A (Turkmen, course 1)
        cur('IP-23-A', 'Prog. esaslary', 'LEC', 1, 'Hojayew')
        cur('IP-23-A', 'Prog. lab',      'LAB', 2, 'Hojayew')
        cur('IP-23-A', 'Mat. analiz',    'LEC', 1, 'Rahimowa')
        cur('IP-23-A', 'Fizika',         'LEC', 1, 'Baýramow')
        cur('IP-23-A', 'MGA',            'LEC', 1, 'Garryýew')
        cur('IP-23-A', 'Wep prog.',      'SIM', 1, 'Durdyyew')
        cur('IP-23-A', 'MB',             'SIM', 1, 'Hojayew')

        # IP-23-B (Turkmen, course 1)
        cur('IP-23-B', 'Prog. esaslary', 'LEC', 1, 'Durdyyew')
        cur('IP-23-B', 'Prog. lab',      'LAB', 2, 'Durdyyew')
        cur('IP-23-B', 'Mat. analiz',    'LEC', 1, 'Baýramow')
        cur('IP-23-B', 'Fizika',         'LEC', 1, 'Rahimowa')
        cur('IP-23-B', 'MGA',            'LEC', 1, 'Garryýew')
        cur('IP-23-B', 'Wep prog.',      'SIM', 1, 'Hojayew')

        # MF groups
        cur('MF-22-A', 'Mat. analiz', 'LEC', 1, 'Rahimowa')
        cur('MF-22-A', 'Fizika',      'LEC', 1, 'Baýramow')
        cur('MF-23-A', 'Mat. analiz', 'LEC', 1, 'Rahimowa')
        cur('MF-23-A', 'Fizika',      'LEC', 1, 'Baýramow')

        self.stdout.write(self.style.SUCCESS(
            f'Okuw plany: {Curriculum.objects.count()} ýazgy goşuldy.'
        ))
