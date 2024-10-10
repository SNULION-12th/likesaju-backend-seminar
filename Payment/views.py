# Create your views here.
from django.shortcuts import render

### 필요한 모듈 불러오기
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from UserProfile.models import UserProfile
import requests
import json

### 등록된 환경변수 정보 가져오기
from django.conf import settings

from django.http import JsonResponse

### 환경변수로 등록된 값 중, KAKAO_PAY_KEY 값 가져와 변수에 넣기
pay_key = settings.KAKAO_PAY_KEY

### 결제 준비 API 요청 URL 정의하기
payready_url = 'https://open-api.kakaopay.com/online/v1/payment/ready'
### 이건 나중에 결제 승인 API 요청시 사용될 URL !
payapprove_url = 'https://open-api.kakaopay.com/online/v1/payment/approve'

pay_header = {
    'Content-Type': 'application/json',
    'Authorization': f'SECRET_KEY {pay_key}'
}

class PayReadyView(APIView):
    def post(self, request):
        pay_data = request.data

        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        pay_data = json.dumps(pay_data)

        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()

				### 🔻 이 부분 추가 ###
        if response.status_code == 200:
            Payment.objects.create(
                tid=response_data['tid'],
                partner_order_id=request.data['partner_order_id'],
                partner_user_id=request.data['partner_user_id'],
                point=request.data['item_name'],
                price=request.data['total_amount'],
                user=user
            )

        return Response(response.json(), status=response.status_code)


class PayApproveView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        pg_token = request.data['pg_token']
        tid = request.data['tid']
        cid = request.data['cid']
        
        pay_hist = Payment.objects.get(tid=tid)
        pay_data = {
            'cid': cid,
            'tid': tid,
            'partner_order_id': pay_hist.partner_order_id,
            'partner_user_id': pay_hist.partner_user_id,
            'pg_token': pg_token
        }
        pay_data = json.dumps(pay_data)
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

				### 🔻 이 부분 추가 ###
        if response.status_code == 200:
            pay_hist.pay_status = 'approved'
            userprofile = UserProfile.objects.get(user=user)
            userprofile.remaining_points+= int(pay_hist.point)
            pay_hist.save()
            userprofile.save()

        return Response(response.json(), status=response.status_code)

# 주문 조회 요청
class PayRecordView(APIView):
    def post(self, request):
        try:
            # request.body에서 JSON 데이터 파싱
            data = json.loads(request.body)
            tid = request.data['tid']
            cid = request.data['cid']

            print(cid, tid)

            if not cid or not tid:
                return JsonResponse({"error": "Missing cid or tid"}, status=400)

            url = "https://open-api.kakaopay.com/online/v1/payment/order"

            # 카카오페이 API로 요청
            payload = {
                "cid": cid,
                "tid": tid,
            }

            print(payload)
            print(requests)


            response = requests.post(url, json=payload, headers=pay_header)

            print(response)
            # 성공적으로 조회된 경우
            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({"error": "Failed to fetch order info"}, status=response.status_code)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)