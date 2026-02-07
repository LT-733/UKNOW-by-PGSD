from django.shortcuts import render


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
    gpa = request.GET.get("gpa")
    uni = request.GET.get("uni")

    return render(request, "frontendapp/result.html")

def detail(request):
    id = request.GET.get("id")

    return render(request, "frontendapp/detail.html")