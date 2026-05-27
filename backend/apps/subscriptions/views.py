from rest_framework.views import APIView
from rest_framework.response import Response


class SubscriptionStatusAPIView(APIView):
    def get(self, request):
        return Response({
            "plan": "FREE",
            "queries_left": 10
        })
