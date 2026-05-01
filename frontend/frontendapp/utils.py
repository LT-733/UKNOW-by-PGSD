import base64
from io import BytesIO

import matplotlib.pyplot as pyplot
from django.db import connection, transaction

def graph_to_img():
    buffer = BytesIO()
    pyplot.savefig(buffer, format='png')
    buffer.seek(0)
    png = buffer.getvalue()
    graph = base64.b64encode(png).decode('utf-8')
    buffer.close()
    return(graph)

def getplot(name, uni):
    sql = "SELECT * FROM grade_results WHERE LOWER(program) LIKE %s"
    params = [f"%{name.lower()}%"]
    sql += " AND university_name = %s"
    params.append(uni)
    sql += " LIMIT 1000"

    avgs = []
    years = []
    try:
        with connection.cursor() as cursor:
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            for row in rows:
                if(row[0] not in years):
                    years.append(row[0])

            years.sort()

            for i in range(len(years)):
                avgs.append(0)
                count = 0
                for row in rows:
                    if(row[0] == years[i]):
                        avgs[i] += row[3]
                        count += 1
                    
                avgs[-1] /= count
            
    except Exception as e:
        print(e)

    if(len(years) == 0):
        return(None)
    #GRAPH FORMATTING GOES HERE
    pyplot.switch_backend('AGG')
    pyplot.figure(figsize = (10, 5))
    pyplot.title("Acceptance Averages By Year")
    pyplot.bar(years, avgs)
    pyplot.xlabel("Year")
    pyplot.ylabel("Average")
    pyplot.xticks(years)
    pyplot.ylim(50, 100)
    pyplot.yticks(range(50,101, 5))
    for p in range(len(avgs)):
        pyplot.annotate(round(avgs[p], 2), xy=(years[p],avgs[p]),
                ha='center',
                va='center',
                xytext=(0, 10),
                textcoords='offset points')
    return graph_to_img()


# --- Shared helpers for HTML views + DRF api/views.py ---

PULL_MAX_ROWS = 500
_SEARCH_LIMIT = 1000


def distinct_university_names():
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT university_name FROM grade_results ORDER BY university_name"
            )
            return [r[0] for r in cursor.fetchall() if r[0]]
    except Exception:
        return []


def aggregated_search_with_risk(program_name, university_name=None, user_avg=None, limit=_SEARCH_LIMIT):
    sql = "SELECT * FROM grade_results WHERE LOWER(program) LIKE %s"
    params = [f"%{program_name.lower()}%"]
    if university_name:
        sql += " AND university_name = %s"
        params.append(university_name)
    sql += " LIMIT %s"
    params.append(limit)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            raw = [dict(zip(cols, r)) for r in cursor.fetchall()]
    except Exception:
        return []

    buckets = []
    for row in raw:
        if row.get("acceptance_status") != "accepted":
            continue
        for b in buckets:
            if row["university_name"] == b[1] and row["program"] == b[0]:
                b[2] = (b[2] * b[3] + row["admission_average"]) / (b[3] + 1)
                b[3] += 1
                break
        else:
            buckets.append([row["program"], row["university_name"], row["admission_average"], 1])

    out = []
    for idx, b in enumerate(buckets, start=1):
        avg_val = round(b[2], 1)
        risk = None
        if user_avg is not None and avg_val is not None:
            diff = user_avg - avg_val
            risk = "match" if abs(diff) <= 3 else ("safe" if diff > 3 else "risky")
        out.append(
            {
                "id": idx,
                "program": b[0],
                "university_name": b[1],
                "admission_average": avg_val,
                "risk": risk,
            }
        )
    return out


def pull_grade_results(program=None, university=None, max_rows=PULL_MAX_ROWS):
    clauses, params = [], []
    if program:
        clauses.append("LOWER(program) LIKE %s")
        params.append(f"%{program.lower()}%")
    if university:
        clauses.append("university_name = %s")
        params.append(university)
    if not clauses:
        return "At least one filter is required", []
    sql = f"SELECT * FROM grade_results WHERE {' AND '.join(clauses)} LIMIT %s"
    params.append(max_rows)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        cols = [c[0] for c in cursor.description]
        return None, [dict(zip(cols, r)) for r in cursor.fetchall()]


def fetch_valid_uni_program_pairs():
    with connection.cursor() as cursor:
        cursor.execute("SELECT university, program FROM program_descriptions")
        return {(r[0].lower(), r[1].lower()) for r in cursor.fetchall()}


def collect_submit_errors(name, gpa, uni, valid_pairs):
    errors = {}
    for key, val in [("name", name), ("gpa", gpa), ("uni", uni)]:
        if not (val or "").strip():
            errors[key] = "This field is required."
    if "gpa" not in errors:
        try:
            gv = float(gpa)
            if gv < 0 or gv > 100:
                errors["gpa"] = "GPA must be between 0 and 100."
        except ValueError:
            errors["gpa"] = "GPA must be a number."
    if not errors and (uni.lower(), name.lower()) not in valid_pairs:
        errors["name"] = "Program name must be valid."
        errors["uni"] = "University name must be valid"
    return errors


def insert_grade_submission(year, program_name, uni, gpa, username):
    sql = (
        "INSERT INTO grade_results (acceptance_year, program, university_name, "
        "admission_average, acceptance_status, userid) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(sql, [year, program_name, uni, gpa, "accepted", username])