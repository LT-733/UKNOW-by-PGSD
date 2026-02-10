from django.shortcuts import render
import requests

def home(request):
    context = {
        "app_name": "UKNOW",
        "tagline": "A university selection lookup table",
        "features": [
            "testing boi"
        ],
    }
    return render(request, "frontendapp/home.html", context)


def result(request):
    name = request.GET.get("name")
    gpa = float(request.GET.get("gpa"))
    uni = request.GET.get("uni")

    if not name or not gpa or not uni:
        return render(request, "frontendapp/result.html", {"error": "Please provide all fields."})

    response = requests.post(
        "http://127.0.0.1:8000/api/pull/",
        json={
            "program": name,
            "average": gpa,
            "university": uni,
        },
        timeout=5,
    )

    results = response.json() if response.status_code == 200 else []
    print(results)

    context = {
        "results": results,
        "program": name,
        "average": gpa,
        "university": uni,
    }

    return render(request, "frontendapp/result.html", context)

def detail(request):
    id = request.GET.get("id")

    return render(request, "frontendapp/detail.html")