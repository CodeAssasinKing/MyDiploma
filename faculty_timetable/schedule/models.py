from django.db import models

DAYS_OF_WEEK = [
    ('MON', 'Duşenbe'),
    ('TUE', 'Sişenbe'),
    ('WED', 'Çarşenbe'),
    ('THU', 'Penşenbe'),
    ('FRI', 'Anna'),
    ('SAT', 'Şenbe'),
    ('SUN', 'Ýekşenbe'),
]

WEEK_TYPES = [
    ('ODD', 'Tak hepde'),
    ('EVEN', 'Jübüt hepde'),
    ('BOTH', 'Her hepde'),
]

CLASSROOM_TYPES = [
    ('LAB', 'Laboratoriya'),
    ('LEC', 'Leksiya zaly'),
    ('SIM', 'Adaty otag'),
]

GROUP_TYPES = [
    ('TM', 'Turkmen'),
    ('EN', 'Inlis'),
    ('RU', 'Rus'),
]

SUBGROUP_TYPES = [
    ('FULL', 'Doly topar'),
    ('SUB1', '1-nji kici topar'),
    ('SUB2', '2-nji kici topar'),
]

LANGUAGE_TYPES = [
    ('TM', 'Turkmence'),
    ('EN', 'Inlisce'),
    ('RU', 'Rusca'),
]


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name='Ady')
    short_name = models.CharField(max_length=20, blank=True, verbose_name='Gysgaca ady')

    class Meta:
        verbose_name = 'Kafedra'
        verbose_name_plural = 'Kafedralar'

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name='Topar ady')
    group_type = models.CharField(max_length=2, choices=GROUP_TYPES, default='TM', verbose_name='Topar gornusi')
    course = models.IntegerField(default=1, verbose_name='Kurs')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Kafedra')
    student_count = models.IntegerField(default=25, verbose_name='Talyp sany')

    class Meta:
        verbose_name = 'Topar'
        verbose_name_plural = 'Toparlar'
        ordering = ['course', 'name']

    def __str__(self):
        return self.name


class Classroom(models.Model):
    name = models.CharField(max_length=50, verbose_name='Otag ady')
    classroom_type = models.CharField(max_length=3, choices=CLASSROOM_TYPES, verbose_name='Otag gornusi')
    capacity = models.IntegerField(default=30, verbose_name='Kuwwatlylygy')
    building = models.CharField(max_length=50, blank=True, verbose_name='Bina')

    class Meta:
        verbose_name = 'Synp otagy'
        verbose_name_plural = 'Synp otaglary'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_classroom_type_display()})"


class Teacher(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Ady')
    last_name = models.CharField(max_length=100, verbose_name='Familiyasy')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Atasyn ady')
    can_teach_english = models.BooleanField(default=False, verbose_name='Inlisce okadyp bilyar')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Kafedra')
    position = models.CharField(max_length=100, blank=True, verbose_name='Wezipesi')

    class Meta:
        verbose_name = 'Mugallym'
        verbose_name_plural = 'Mugallymlar'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name[0]}."

    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts)


class Subject(models.Model):
    name = models.CharField(max_length=200, verbose_name='Dersinin ady')
    short_name = models.CharField(max_length=50, blank=True, verbose_name='Gysgaca ady')
    subject_type = models.CharField(max_length=3, choices=CLASSROOM_TYPES, verbose_name='Ders gornusi')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Kafedra')

    class Meta:
        verbose_name = 'Ders'
        verbose_name_plural = 'Dersler'
        ordering = ['name']

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    number = models.IntegerField(verbose_name='Jubet belgisi')
    start_time = models.TimeField(verbose_name='Baslanyan wagty')
    end_time = models.TimeField(verbose_name='Gutaryan wagty')
    shift = models.IntegerField(default=1, verbose_name='Calsyk', choices=[(1, '1-nji calsyk'), (2, '2-nji calsyk')])

    class Meta:
        verbose_name = 'Wagt jubudi'
        verbose_name_plural = 'Wagt jubetleri'
        ordering = ['number']

    def __str__(self):
        return f"{self.number}-nji jubet {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

    def time_range(self):
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Ders')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Mugallym')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Topar')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name='Synp otagy')
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK, verbose_name='Gun')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name='Wagt jubudi')
    week_type = models.CharField(max_length=4, choices=WEEK_TYPES, default='BOTH', verbose_name='Hepde gornusi')
    subgroup = models.CharField(max_length=4, choices=SUBGROUP_TYPES, default='FULL', verbose_name='Kici topar')
    lesson_type = models.CharField(max_length=3, choices=CLASSROOM_TYPES, verbose_name='Sapak gornusi')
    language = models.CharField(max_length=2, choices=LANGUAGE_TYPES, default='TM', verbose_name='Dil')

    class Meta:
        verbose_name = 'Sapak'
        verbose_name_plural = 'Sapaklyk'

    def __str__(self):
        return f"{self.subject} - {self.group} - {self.get_day_display()}"

    def type_css_class(self):
        classes = {'LAB': 'lesson-lab', 'LEC': 'lesson-lec', 'SIM': 'lesson-sim'}
        return classes.get(self.lesson_type, 'lesson-sim')


class Curriculum(models.Model):
    """Defines what a group must study: group + subject + how many times per week."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Topar', related_name='curriculum')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Ders')
    lesson_type = models.CharField(max_length=3, choices=CLASSROOM_TYPES, verbose_name='Sapak gornusi')
    hours_per_week = models.IntegerField(default=1, verbose_name='Hepde jubutleri',
        help_text='BOTH hepde ucin 1, LAB ucin 2 (tak+juft)')
    preferred_teacher = models.ForeignKey(
        Teacher, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Saylanyan mugallym'
    )

    class Meta:
        verbose_name = 'Okuw plany'
        verbose_name_plural = 'Okuw planlary'
        unique_together = ('group', 'subject', 'lesson_type')

    def __str__(self):
        return f"{self.group} | {self.subject} | {self.get_lesson_type_display()} x{self.hours_per_week}"
