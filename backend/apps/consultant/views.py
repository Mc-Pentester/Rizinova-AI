from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.orchestrator import ConsultantOrchestrator
from .models import ConsultantSession

class ConsultantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get("query")
        data = request.data.get("data", {})

        orchestrator = ConsultantOrchestrator()
        result = orchestrator.handle(
            user=request.user,
            query=query,
            data=data,
            plan="pro"
        )

        ConsultantSession.objects.create(
            user=request.user,
            query=query,
            intent=result.get("type", "unknown"),
            response_json=result
        )

        return Response(result)