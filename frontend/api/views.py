from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection


@api_view(['POST'])
def pull(request):
    uniname = request.data.get('university')
    average = request.data.get('average')
    program = request.data.get('program')

    returnout = []
    PULL_MESSAGE = ""

    if program is not None and uniname is not None and average is not None:
        PULL_MESSAGE = """
            SELECT * FROM grade_results 
            WHERE program ILIKE %s 
            AND admission_average = %s 
            AND university_name = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(PULL_MESSAGE, [f"%{program}%", average, uniname])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            returnout = [dict(zip(columns, row)) for row in rows]

    elif program and average:
        PULL_MESSAGE = """
            SELECT * FROM grade_results 
            WHERE program ILIKE %s 
            AND admission_average = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(PULL_MESSAGE, [f"%{program}%", average])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            returnout = [dict(zip(columns, row)) for row in rows]

    elif uniname and program:
        PULL_MESSAGE = """
            SELECT * FROM grade_results 
            WHERE program ILIKE %s 
            AND university_name = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(PULL_MESSAGE, [f"%{program}%", uniname])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            returnout = [dict(zip(columns, row)) for row in rows]

    elif uniname and average:
        PULL_MESSAGE = """
            SELECT * FROM grade_results 
            WHERE university_name = %s 
            AND admission_average = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(PULL_MESSAGE, [uniname, average])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            returnout = [dict(zip(columns, row)) for row in rows]

    else:
        return Response(
            {"error": "At least two filters are required"},
            status=400
        )

    return Response(returnout)
