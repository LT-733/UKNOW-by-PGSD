from django.shortcuts import render


def home(request):
    context = {
        "app_name": "UKNOW",
        "tagline": "A basic Django app",
        "features": [
            "testing boi"
        ],
    }
    return render(request, "frontendapp/home.html", context)
