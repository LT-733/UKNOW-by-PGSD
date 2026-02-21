from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator
import requests
from .utils import getplot


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
            newresults = []
            for row in results:
                if(row['acceptance_status'] == 'accepted'):
                    flag = True
                    for new in newresults:
                        if(row['university_name'] == new[1]):
                            new[2] = (new[2] * new[3] + row['admission_average'])/(new[3] + 1)
                            new[3] += 1
                            flag = False

                    if(flag):
                        newresults.append([row['program'], row['university_name'], row['admission_average'], 1])

            for new in newresults:
                new[2] = round(new[2], 1)

            results = [dict(zip(cols[1:3], new[:-1])) for new in newresults]

    except Exception as e:
        print(e)
        results = []

    paginator = Paginator(results, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'program': name,
        'university': uni,
    }

    return render(request, 'frontendapp/result.html', context)

def detail(request):
    id = request.GET.get("id")
    name = "Software Engineering"#request.GET.get("name")
    uni = "University of Waterloo"#request.GET.get("uni")
    graph = getplot(name, uni)
    return render(request, "frontendapp/detail.html", {'graph': graph})