from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator
from datetime import datetime
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
    gpa = request.GET.get("gpa")
    # parse user's average (supports ?avg= or ?average= or ?score=)
    user_avg = None
    avg_param = gpa or request.GET.get('avg') or request.GET.get('average') or request.GET.get('score')
    if avg_param:
        try:
            user_avg = float(avg_param)
        except Exception:
            user_avg = None

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
                        if(row['university_name'] == new[1] and row['program'] == new[0]):
                            new[2] = (new[2] * new[3] + row['admission_average'])/(new[3] + 1)
                            new[3] += 1
                            flag = False

                    if(flag):
                        newresults.append([row['program'], row['university_name'], row['admission_average'], 1])

            for new in newresults:
                new[2] = round(new[2], 1)

            results = []
            for idx, new in enumerate(newresults, start=1):
                avg_val = new[2]
                risk = None
                try:
                    if user_avg is not None and avg_val is not None:
                        diff = user_avg - avg_val
                        if abs(diff) <= 3:
                            risk = 'match'
                        elif diff > 3:
                            risk = 'safe'
                        else:
                            risk = 'risky'
                except Exception:
                    risk = None

                results.append({
                    'id': idx,
                    'program': new[0],
                    'university_name': new[1],
                    'admission_average': avg_val,
                    'risk': risk,
                })

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
        'gpa': avg_param,
    }

    return render(request, 'frontendapp/result.html', context)

def detail(request):
    #id = request.GET.get("id")
    name = request.GET.get("name")
    uni = request.GET.get("uni")
    msg = "SELECT * FROM program_descriptions WHERE LOWER(university) LIKE %s AND LOWER(program) LIKE %s"
    description = ""
    link = ""
    graph = getplot(name, uni)
    try:
        with connection.cursor() as cursor:
            cursor.execute(msg, [f"%{uni.lower()}%", f"%{name.lower()}%"])
            #cursor.execute(msg, uni.lower(), name.lower())
            rows = cursor.fetchall()
            if not rows:
                print(f"no data found")
                raise Exception
            description += rows[0][2].encode("latin1").decode("utf-8")
            link += rows[0][3]


    except Exception as e:
        print(f"database error: {e}")
        #return 1
    
    return render(request, "frontendapp/detail.html", {
        'graph': graph,
        'university': uni, 
        'name': name, 
        'description': description, 
        'link': link
    })

def submit(request):
    auto_username = "anonymous"
    if getattr(request, "user", None) and request.user.is_authenticated:
        auto_username = request.user.get_username() or "anonymous"
    auto_year = str(datetime.now().year)

    form_data = {
        "username": auto_username,
        "year": auto_year,
        "name": "",
        "gpa": "",
        "uni": "",
    }
    errors = {}
    success = False

    if request.method == "POST":
        form_data["username"] = auto_username
        form_data["year"] = auto_year
        form_data["name"] = request.POST.get("name", "").strip()
        form_data["gpa"] = request.POST.get("gpa", "").strip()
        form_data["uni"] = request.POST.get("uni", "").strip()

        for key in ["name", "gpa", "uni"]:
            if not form_data[key]:
                errors[key] = "This field is required."

        if "gpa" not in errors:
            try:
                gpa_value = float(form_data["gpa"])
                if gpa_value < 0 or gpa_value > 100:
                    errors["gpa"] = "GPA must be between 0 and 100."
            except ValueError:
                errors["gpa"] = "GPA must be a number."

        success = not errors

    return render(
        request,
        "frontendapp/submit.html",
        {
            "form_data": form_data,
            "errors": errors,
            "success": success,
        },
    )
