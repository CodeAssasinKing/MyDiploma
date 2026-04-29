#!/bin/bash
# Fakultet Sapaklyk Ulgamy — Çalt Başlatmak Skripti

echo "======================================"
echo "  Fakultet Sapaklyk Ulgamy"
echo "  Gurnamak we Işletmek"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ÝALŇYŞ] Python3 tapylmady. Gurnaň."
    exit 1
fi

echo "[1/4] Virtual environment döredilýär..."
python3 -m venv venv
source venv/bin/activate

echo "[2/4] Django gurulýar..."
pip install django --quiet

echo "[3/4] Maglumat bazasy göçürilýär..."
python manage.py migrate --run-syncdb

echo "[4/4] Nusga maglumatlary ýüklenýär..."
python manage.py seed_data

echo ""
echo "[OK] Admin ulanyjy döredilýär: admin / admin1234"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@faculty.tm','admin1234')" | python manage.py shell --no-color

echo ""
echo "======================================"
echo "  Başladyldy! Açyň:"
echo "  http://127.0.0.1:8000/"
echo "======================================"
python manage.py runserver
