from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from frontendapp.utils import (
    PULL_MAX_ROWS,
    aggregated_search_with_risk,
    distinct_university_names,
    pull_grade_results,
)


class SearchSerializer(serializers.Serializer):
    """Same search shape as the HTML result page, but via JSON body."""

    program = serializers.CharField(required=True, trim_whitespace=True)
    university = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    user_average = serializers.FloatField(required=False, allow_null=True)


# under GET, we write a short test
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test_api(request):
    return Response(
        {
            "message": "OAuth works",
            "user": str(request.user),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def universities_list(request):
    """Distinct university names (same source as the home page)."""
    return Response(distinct_university_names())


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_programs(request):
    """
    Aggregated search like /result/: accepted rows averaged by program + university,
    optional risk labels vs user_average.
    """
    ser = SearchSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    program = ser.validated_data["program"]
    university = (ser.validated_data.get("university") or "").strip() or None
    user_avg = ser.validated_data.get("user_average")
    results = aggregated_search_with_risk(program, university, user_avg)
    return Response({"count": len(results), "results": results})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pull(request):
    uniname = request.data.get("university")
    program = request.data.get("program")

    err, returnout = pull_grade_results(
        program=program,
        university=uniname,
        max_rows=PULL_MAX_ROWS,
    )
    if err:
        return Response({"error": err}, status=400)

    return Response(returnout)
