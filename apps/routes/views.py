from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.routes.serializers import FuelPlanRequestSerializer
from apps.routes.services.geocoding_service import (
    GeocodingServiceUnavailableError,
    GeocodingTimeoutError,
    LocationNotFoundError,
)
from apps.routes.services.fuel_plan_service import FuelPlanService
from apps.routes.services.routing_service import (
    RouteNotFoundError,
    RoutingServiceUnavailableError,
    RoutingTimeoutError,
)


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
        except LocationNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except RouteNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except (GeocodingTimeoutError, RoutingTimeoutError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except (GeocodingServiceUnavailableError, RoutingServiceUnavailableError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(payload)
