# Fakultet Sapaklyk Ulgamy
**Faculty Timetable System — Turkmen Language Interface**

## Taslama barada (About the Project)

Django bilen gurlan fakultetiň sapaklyk ulgamy. Ähli interfeýs **türkmen dilinde**.

### Esasy Aýratynlyklar

- **Hemme toparlar sapaklyk** — sütünlerde toparlar, setirde günler we wagt jübütleri
- **Täk/Jüft hepde** — laboratoriýa sapaklary üçin aýratyn görnüş
- **Laboratoriýa sapaklar** — topar iki kiçi topara (SUB1, SUB2) bölünýär
- **2 çalşyk** — günde 6 jübüt: 1-nji çalşyk 08:30-13:20, 2-nji çalşyk 14:00-18:50
- **Mugallym sapaklyk** — her mugallymyň şahsy sapaklyk jüpüdi
- **Otag sapaklyk** — synp otaglarynyň iş tertibi
- **Topar sapaklyk** — her toparyň jikme-jik sapaklyk tertibi
- **Iňlis/Türkmen toparlar** — iňlis dilinde okadyp bilýän mugallymlar bellenilendir
- **Çap etmek** — sapaklyk tablisasyny çap etmek mümkinçiligi
- **Django Admin** — maglumatlary dolandyrmak üçin doly panel
- **Jogaply dizaýn** — mobil enjamlar üçin goldaw

### Otag Görnüşleri
| Görnüş | Düşündiriş |
|--------|-----------|
| 🔬 Laboratoriýa | Laboratoriýa otag — diňe lab. sapaklary üçin |
| 📢 Leksiýa zaly | Uly leksiýa zaly (100–120 orun) |
| 📖 Adaty otag | Adaty synp otagy |

### Sapak Görnüşleri
| Görnüş | Reňk | Düşündiriş |
|--------|------|-----------|
| Laboratoriýa | Gyrmyzy-mor | Täk/Jüft hepde, 2 kiçi topar |
| Leksiýa | Gök | Doly topar bilen |
| Adaty | Ýaşyl | Adaty sapak |

---

## Gurnamak (Installation)

### Talaplar
- Python 3.10+
- pip

### Ädimler

```bash
# 1. Klonla ýa-da zip açyk
cd faculty_timetable

# 2. Virtual environment döret
python -m venv venv
source venv/bin/activate        # Linux/Mac
# ýa-da
venv\Scripts\activate           # Windows

# 3. Gerekli paketleri gurnaw
pip install django

# 4. Maglumat bazasyny döret
python manage.py migrate

# 5. Nusga maglumatlary ýükle
python manage.py seed_data

# 6. Admin ulanyjy döret
python manage.py createsuperuser
# ýa-da bar bolan: admin / admin1234

# 7. Serweri işlet
python manage.py runserver
```

Soňra brauzerde açyň: http://127.0.0.1:8000/

---

## Salgylar (URLs)

| Salgy | Sahypa |
|-------|--------|
| `/` | Baş sahypa (statistika + toparlar) |
| `/sapaklyk/` | Hemme toparlar sapaklyk |
| `/mugallymlar/` | Mugallymlar sanawy |
| `/mugallymlar/<id>/` | Mugallymyň sapaklyk tertibi |
| `/otaglar/` | Synp otaglary sanawy |
| `/otaglar/<id>/` | Otagyň iş tertibi |
| `/toparlar/<id>/` | Toparyň sapaklyk tertibi |
| `/admin/` | Django dolandyryjy paneli |

---

## Maglumat Modelleri (Data Models)

```
Department (Kafedra)
    └── Group (Topar) — görnüşi: TM/EN/RU, kursy
    └── Teacher (Mugallym) — iňlis dilinde okadyp bilýär
    └── Subject (Ders) — görnüşi: LAB/LEC/SIM

TimeSlot (Wagt jübüdi) — 1-6 jübüt, 2 çalşyk

Lesson (Sapak)
    ├── Subject, Teacher, Group, Classroom
    ├── day: MON..SUN
    ├── time_slot: 1..6
    ├── week_type: ODD | EVEN | BOTH
    ├── subgroup: FULL | SUB1 | SUB2
    ├── lesson_type: LAB | LEC | SIM
    └── language: TM | EN | RU
```

---

## Admin Giriş
- URL: http://127.0.0.1:8000/admin/
- Ulanyjy: `admin`
- Açar söz: `admin1234`

---

## Diplom işi üçin bellikler

Bu taslama şu mümkinçilikleri görkezýär:
1. Django ORM bilen çylşyrymly maglumat modelleri
2. Köp baglanyşykly sorgulamalar (select_related)
3. Çylşyrymly wagt we hepde görnüşine esaslanýan süzgüç logikasy
4. Doly jogaply CSS dizaýny (sidebar, kartylar, jadwal tablisasy)
5. Çap etmek media sorgulary
6. Management command bilen seed data
