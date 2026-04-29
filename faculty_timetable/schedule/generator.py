"""
schedule/generator.py
=====================
Automatic timetable generator using a greedy + constraint-satisfaction approach.

Constraints honoured:
  - A teacher cannot be in two places at the same (day, slot, week).
  - A classroom cannot host two lessons at the same (day, slot, week).
  - A group (or sub-group) cannot have two lessons at the same (day, slot, week).
  - LAB lessons go only into LAB classrooms.
  - LEC lessons go only into LEC classrooms.
  - SIM lessons go into SIM classrooms.
  - English groups get only English-capable teachers.
  - LAB lessons are split into SUB1 (ODD) + SUB2 (EVEN) pairs.
  - Lessons are spread evenly across days and shifts.
"""

import random
from collections import defaultdict
from .models import (
    Group, Teacher, Classroom, Subject, TimeSlot, Lesson,
    Curriculum, DAYS_OF_WEEK,
)


DAYS = [d[0] for d in DAYS_OF_WEEK]   # MON..SUN


class GeneratorError(Exception):
    pass


class TimetableGenerator:
    def __init__(self, group_ids=None, clear_existing=False, max_daily_lessons=4, preferred_days=None):
        """
        group_ids       – list of Group PKs to schedule; None = all groups
        clear_existing  – wipe existing Lesson rows for these groups first
        max_daily_lessons – soft cap on lessons per group per day
        preferred_days  – list of day codes to use (default: all 6 working days)
        """
        self.group_ids        = group_ids
        self.clear_existing   = clear_existing
        self.max_daily_lessons = max_daily_lessons
        self.preferred_days   = preferred_days or ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

        # ── Load database objects ──────────────────────────────
        self.time_slots  = list(TimeSlot.objects.order_by('number'))
        self.groups      = list(Group.objects.filter(pk__in=group_ids).select_related('department')
                                if group_ids else Group.objects.all().select_related('department'))
        self.teachers    = list(Teacher.objects.all())
        self.classrooms  = {
            'LAB': list(Classroom.objects.filter(classroom_type='LAB')),
            'LEC': list(Classroom.objects.filter(classroom_type='LEC')),
            'SIM': list(Classroom.objects.filter(classroom_type='SIM')),
        }

        if not self.time_slots:
            raise GeneratorError("Wagt jübütleri tapylmady. Ilki wagt jübütlerini goşuň.")
        if not self.groups:
            raise GeneratorError("Topar tapylmady.")

        # ── Occupancy sets (fast conflict detection) ───────────
        # teacher_busy[(day, slot_id, week)] = set of teacher_ids
        # room_busy[(day, slot_id, week)]    = set of classroom_ids
        # group_busy[(day, slot_id, week, group_id, subgroup)] = bool
        self.teacher_busy  = defaultdict(set)
        self.room_busy     = defaultdict(set)
        self.group_busy    = defaultdict(bool)

        # Pre-load existing lessons for groups NOT in our set
        existing_qs = Lesson.objects.select_related('teacher', 'classroom', 'group', 'time_slot')
        if group_ids and not clear_existing:
            existing_qs = existing_qs.exclude(group_id__in=group_ids)

        for les in existing_qs:
            for wk in self._expand_week(les.week_type):
                key = (les.day, les.time_slot_id, wk)
                self.teacher_busy[key].add(les.teacher_id)
                self.room_busy[key].add(les.classroom_id)
                sg = les.subgroup
                self.group_busy[(les.day, les.time_slot_id, wk, les.group_id, sg)] = True
                if sg != 'FULL':
                    self.group_busy[(les.day, les.time_slot_id, wk, les.group_id, 'FULL')] = True
                else:
                    self.group_busy[(les.day, les.time_slot_id, wk, les.group_id, 'SUB1')] = True
                    self.group_busy[(les.day, les.time_slot_id, wk, les.group_id, 'SUB2')] = True

        # daily lesson count per group  {(group_id, day): count}
        self.daily_count = defaultdict(int)

        # Results
        self.created   = []   # Lesson objects to bulk-create
        self.skipped   = []   # (curriculum_item, reason) tuples
        self.warnings  = []

    # ── Public entry point ────────────────────────────────────

    def run(self):
        """Run the generator. Returns (created_count, skipped_list, warnings_list)."""
        group_ids = [g.pk for g in self.groups]

        if self.clear_existing:
            deleted, _ = Lesson.objects.filter(group_id__in=group_ids).delete()
            self.warnings.append(f"{deleted} sany öňki sapak pozuldy.")

        # Load curricula ordered: LAB first (most constrained), then LEC, then SIM
        curricula = list(
            Curriculum.objects.filter(group__in=self.groups)
            .select_related('group', 'subject', 'preferred_teacher')
            .order_by(
                # LAB=0, LEC=1, SIM=2 for ordering
                'lesson_type',
                'group__course',
                'group__name',
            )
        )

        if not curricula:
            raise GeneratorError(
                "Okuw plany tapylmady. Ilki 'Okuw Plany' bölümünden dersler goşuň."
            )

        for cur in curricula:
            self._schedule_curriculum(cur)

        # Bulk create
        Lesson.objects.bulk_create(self.created, ignore_conflicts=True)
        return len(self.created), self.skipped, self.warnings

    # ── Per-curriculum scheduling ─────────────────────────────

    def _schedule_curriculum(self, cur):
        group       = cur.group
        subject     = cur.subject
        ltype       = cur.lesson_type
        hours       = cur.hours_per_week
        pref_teacher = cur.preferred_teacher

        # Pick teacher
        teacher = self._pick_teacher(group, pref_teacher, ltype)
        if teacher is None:
            self.skipped.append((str(cur), "Elýeterli mugallym tapylmady"))
            return

        if ltype == 'LAB':
            # LAB = SUB1/ODD + SUB2/EVEN  (two classroom slots per pair)
            pairs_needed = max(1, hours // 2) if hours > 1 else 1
            for _ in range(pairs_needed):
                slot = self._find_slot(group, teacher, 'LAB', week='ODD',  subgroup='SUB1')
                if slot:
                    day, ts, room = slot
                    self._book(day, ts, 'ODD', group, teacher, room, subject, 'LAB', 'SUB1')
                    # SUB2 gets EVEN on the same day+timeslot if possible, else next free
                    slot2 = self._find_slot(group, teacher, 'LAB', week='EVEN', subgroup='SUB2',
                                            prefer_day=day, prefer_ts=ts)
                    if slot2:
                        day2, ts2, room2 = slot2
                        self._book(day2, ts2, 'EVEN', group, teacher, room2, subject, 'LAB', 'SUB2')
                    else:
                        self.warnings.append(
                            f"{group} | {subject}: SUB2 (EVEN) üçin slot tapylmady"
                        )
                else:
                    self.skipped.append((str(cur), "Lab üçin boş slot tapylmady"))
        else:
            # LEC / SIM — BOTH week, FULL group
            for _ in range(hours):
                slot = self._find_slot(group, teacher, ltype, week='BOTH', subgroup='FULL')
                if slot:
                    day, ts, room = slot
                    self._book(day, ts, 'BOTH', group, teacher, room, subject, ltype, 'FULL')
                else:
                    self.skipped.append((str(cur), f"{ltype} üçin boş slot tapylmady"))

    # ── Conflict-free slot search ─────────────────────────────

    def _find_slot(self, group, teacher, ltype, week, subgroup,
                   prefer_day=None, prefer_ts=None):
        """
        Find (day, timeslot, classroom) with no conflicts.
        Returns None if nothing found.
        """
        rooms = list(self.classrooms.get(ltype, []))
        if not rooms:
            return None

        weeks_to_check = self._expand_week(week)

        # Build candidate list: prefer preferred_day/ts first, then others
        candidates = []
        if prefer_day and prefer_ts:
            candidates.append((prefer_day, prefer_ts))

        for day in self.preferred_days:
            for ts in self.time_slots:
                if (day, ts) not in [(c[0], c[1]) for c in candidates]:
                    candidates.append((day, ts))

        for day, ts in candidates:
            # Soft cap on daily lessons per group
            if self.daily_count[(group.pk, day)] >= self.max_daily_lessons:
                continue

            # Check group free
            if not self._group_free(day, ts.pk, weeks_to_check, group.pk, subgroup):
                continue

            # Check teacher free
            if not self._teacher_free(day, ts.pk, weeks_to_check, teacher.pk):
                continue

            # Find a free room of the right type
            random.shuffle(rooms)
            for room in rooms:
                if self._room_free(day, ts.pk, weeks_to_check, room.pk):
                    return (day, ts, room)

        return None

    # ── Booking ───────────────────────────────────────────────

    def _book(self, day, ts, week_type, group, teacher, room, subject, ltype, subgroup):
        lang = 'EN' if group.group_type == 'EN' else 'TM'
        lesson = Lesson(
            subject=subject,
            teacher=teacher,
            group=group,
            classroom=room,
            day=day,
            time_slot=ts,
            week_type=week_type,
            subgroup=subgroup,
            lesson_type=ltype,
            language=lang,
        )
        self.created.append(lesson)

        # Mark busy
        for wk in self._expand_week(week_type):
            key = (day, ts.pk, wk)
            self.teacher_busy[key].add(teacher.pk)
            self.room_busy[key].add(room.pk)
            self.group_busy[(day, ts.pk, wk, group.pk, subgroup)] = True
            if subgroup == 'FULL':
                self.group_busy[(day, ts.pk, wk, group.pk, 'SUB1')] = True
                self.group_busy[(day, ts.pk, wk, group.pk, 'SUB2')] = True
            else:
                self.group_busy[(day, ts.pk, wk, group.pk, 'FULL')] = True

        self.daily_count[(group.pk, day)] += 1

    # ── Conflict checks ───────────────────────────────────────

    def _group_free(self, day, slot_id, weeks, group_id, subgroup):
        for wk in weeks:
            if self.group_busy.get((day, slot_id, wk, group_id, subgroup)):
                return False
            if subgroup == 'FULL':
                if self.group_busy.get((day, slot_id, wk, group_id, 'SUB1')):
                    return False
                if self.group_busy.get((day, slot_id, wk, group_id, 'SUB2')):
                    return False
            else:
                if self.group_busy.get((day, slot_id, wk, group_id, 'FULL')):
                    return False
        return True

    def _teacher_free(self, day, slot_id, weeks, teacher_id):
        for wk in weeks:
            if teacher_id in self.teacher_busy.get((day, slot_id, wk), set()):
                return False
        return True

    def _room_free(self, day, slot_id, weeks, room_id):
        for wk in weeks:
            if room_id in self.room_busy.get((day, slot_id, wk), set()):
                return False
        return True

    # ── Teacher picking ───────────────────────────────────────

    def _pick_teacher(self, group, preferred, ltype):
        # Try preferred first
        if preferred:
            if self._teacher_eligible(preferred, group):
                return preferred

        # Filter eligible teachers
        dept = group.department
        candidates = [
            t for t in self.teachers
            if t.department_id == dept.pk and self._teacher_eligible(t, group)
        ]
        # Fallback: any eligible teacher across departments
        if not candidates:
            candidates = [t for t in self.teachers if self._teacher_eligible(t, group)]

        if not candidates:
            return None

        # Pick least-loaded teacher (spread load evenly)
        teacher_load = defaultdict(int)
        for les in self.created:
            teacher_load[les.teacher_id] += 1
        candidates.sort(key=lambda t: teacher_load[t.pk])
        return candidates[0]

    def _teacher_eligible(self, teacher, group):
        if group.group_type == 'EN' and not teacher.can_teach_english:
            return False
        return True

    # ── Helper ────────────────────────────────────────────────

    @staticmethod
    def _expand_week(week_type):
        """Return list of concrete week codes this week_type covers."""
        if week_type == 'BOTH':
            return ['ODD', 'EVEN']
        return [week_type]
