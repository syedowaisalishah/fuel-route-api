from rest_framework.response import Response
from rest_framework.views import APIView

from apps.routes.serializers import FuelPlanRequestSerializer
from apps.routes.services.geocoding_service import LocationLookupError
from apps.routes.services.fuel_plan_service import FuelPlanService
from apps.routes.services.routing_service import RouteLookupError


class ApiRootView(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Fuel route API is running.",
                "version": "0.1.0",
            }
        )


class FuelPlanView(APIView):
    def post(self, request):
        serializer = FuelPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payload = FuelPlanService().build_plan(
                start=serializer.validated_data["start"],
                finish=serializer.validated_data["finish"],
                include_geometry=serializer.validated_data["include_geometry"],
            )
        except LocationLookupError as exc:
            return Response({"detail": str(exc)}, status=400)
        except RouteLookupError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response(payload)
