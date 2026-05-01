import base64
import hashlib
import os
import secrets
from datetime import datetime
from urllib.parse import urlencode

import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .utils import (
    aggregated_search_with_risk,
    collect_submit_errors,
    distinct_university_names,
    fetch_valid_uni_program_pairs,
    getplot,
    insert_grade_submission,
)

def auth_page(request):
    login_form = AuthenticationForm(request, data=request.POST or None)
    register_form = UserCreationForm(request.POST or None)
    context = {
        'login_form': login_form,
        'register_form': register_form,
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login' and login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect('home')
        elif action == 'register' and register_form.is_valid():
            user = register_form.save()
            login(request, user)
            return redirect('home')

    return render(request, 'frontendapp/login.html', context)


def _public_base_url(request):
    protocol = (
        "https"
        if not request.get_host().startswith("127.0.0.1")
        and not request.get_host().startswith("localhost")
        else "http"
    )
    return f"{protocol}://{request.get_host()}"


def _pkce_pair():
    """RFC 7636 S256: verifier and challenge (base64url, no padding)."""
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def oauth_pkce_start(request):
    """
    Store PKCE verifier and state in session, then redirect to django-oauth-toolkit authorize.
    OAuth flows must begin here so the callback can validate state and supply code_verifier.
    """
    client_id = os.environ.get("OAUTH_CLIENT_ID")
    if not client_id:
        return JsonResponse({"error": "OAuth client is not configured."}, status=500)

    base_url = _public_base_url(request)
    redirect_uri = f"{base_url}/auth/callback/"
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(32)
    request.session["oauth_pkce_verifier"] = verifier
    request.session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid profile email",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return redirect(f"{base_url}/o/authorize/?{urlencode(params)}")


def oauth_callback(request):
    base_url = _public_base_url(request)
    token_url = f"{base_url}/o/token/"

    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Invalid authorization response."}, status=400)

    state_param = request.GET.get("state")
    expected_state = request.session.pop("oauth_state", None)
    code_verifier = request.session.pop("oauth_pkce_verifier", None)

    if (
        not state_param
        or not expected_state
        or not secrets.compare_digest(state_param, expected_state)
        or not code_verifier
    ):
        return JsonResponse({"error": "Invalid or expired OAuth session."}, status=400)

    client_id = os.environ.get("OAUTH_CLIENT_ID")
    client_secret = os.environ.get("OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        return JsonResponse({"error": "OAuth client is not configured."}, status=500)

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f"{base_url}/auth/callback/",
        "code_verifier": code_verifier,
    }

    try:
        response = requests.post(token_url, data=payload, timeout=30)
    except requests.RequestException:
        return JsonResponse(
            {"error": "Token request failed. Try again later."},
            status=502,
        )

    try:
        body = response.json()
    except ValueError:
        return JsonResponse({"error": "Invalid token server response."}, status=502)

    if response.status_code >= 400:
        return JsonResponse(
            {"error": "Authorization failed.", "details": body},
            status=response.status_code,
        )

    return JsonResponse(body)


def home(request):
    universities = distinct_university_names()

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

    results = aggregated_search_with_risk(name, uni or None, user_avg)

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
@login_required(login_url='login')
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

        valid_pairs = fetch_valid_uni_program_pairs()
        errors.update(
            collect_submit_errors(
                form_data["name"],
                form_data["gpa"],
                form_data["uni"],
                valid_pairs,
            )
        )

        if not errors:
            try:
                insert_grade_submission(
                    form_data["year"],
                    form_data["name"],
                    form_data["uni"],
                    form_data["gpa"],
                    form_data["username"],
                )
            except Exception as e:
                errors["dberror"] = str(e)

    success = request.method == "POST" and not errors
    return render(
        request,
        "frontendapp/submit.html",
        {
            "form_data": form_data,
            "errors": errors,
            "success": success,
        },
    )
    
@login_required(login_url='login')
def profile(request):
    return render(request, "frontendapp/profile.html")
