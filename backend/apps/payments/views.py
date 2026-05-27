from rest_framework.views import APIView
from rest_framework.response import Response


class CreatePaymentAPIView(APIView):
    def post(self, request):
        return Response({
            "status": "Paiement initié",
            "provider": "Mobile Money / Banque"
        })
