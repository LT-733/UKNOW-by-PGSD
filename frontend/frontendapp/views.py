from django.shortcuts import render
from django.db import connection
import requests


def home(request):
    universities = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT DISTINCT university_name FROM grade_results ORDER BY university_name')
            rows = cursor.fetchall()
            universities = [r[0] for r in rows if r[0]]
    except Exception:
        universities = []

    context = {
        "app_name": "UKNOW",
        "tagline": "A university selection lookup table",
        "features": ["testing boi"],
        "universities": universities,
    }
    return render(request, "frontendapp/home.html", context)


def result(request):
    name = request.GET.get("name")
    uni = request.GET.get("uni")

    if not name:
        return render(request, "frontendapp/result.html", {"error": "Please provide a program name."})

    sql = "SELECT * FROM grade_results WHERE LOWER(program) LIKE %s"
    params = [f"%{name.lower()}%"]
    if uni:
        sql += " AND university_name = %s"
        params.append(uni)
    sql += " LIMIT 1000"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description]
            results = [dict(zip(cols, r)) for r in rows]
    except Exception:
        results = []

    context = {
        'results': results,
        'program': name,
        'university': uni,
    }

    return render(request, 'frontendapp/result.html', context)

def detail(request):
    id = request.GET.get("id")

    return render(request, "frontendapp/detail.html")