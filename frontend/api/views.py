from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection


@api_view(['POST'])
def pull(request):
    uniname = request.data.get('university')
    average = request.data.get('average')
    program = request.data.get('program')

    returnout = []

    # Ignore incoming GPA/average filter; build query only from program and/or
    # university. Program matching is case-insensitive.
    clauses = []
    params = []
    if program:
        clauses.append('LOWER(program) LIKE %s')
        params.append(f"%{program.lower()}%")
    if uniname:
        clauses.append('university_name = %s')
        params.append(uniname)

    if not clauses:
        return Response({"error": "At least one filter is required"}, status=400)

    PULL_MESSAGE = f"SELECT * FROM grade_results WHERE {' AND '.join(clauses)}"
    with connection.cursor() as cursor:
        cursor.execute(PULL_MESSAGE, params)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        returnout = [dict(zip(columns, row)) for row in rows]

    return Response(returnout)
