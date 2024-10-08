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

### 환경변수로 등록된 값 중, KAKAO_PAY_KEY 값 가져와 변수에 넣기
pay_key = settings.KAKAO_PAY_KEY

### 결제 준비 API 요청 URL 정의하기
payready_url = 'https://open-api.kakaopay.com/online/v1/payment/ready'
### 이건 나중에 결제 승인 API 요청시 사용될 URL !
payapprove_url = 'https://open-api.kakaopay.com/online/v1/payment/approve'

payorder_url = 'https://open-api.kakaopay.com/v1/payment/order' 

pay_header = {
    'Content-Type': 'application/json',
    'Authorization': f'SECRET_KEY {pay_key}'
}

class PayReadyView(APIView):
    def post(self, request):
        pay_data = request.data

				#### 2
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        #### 3
        pay_data = json.dumps(pay_data)

				#### 4
        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()
        
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
            return Response({"detail": "please sign in."}, status=status.HTTP_401_UNAUTHORIZED)

        pg_token = request.data['pg_token']
        tid = request.data['tid']
        cid = request.data['cid']
        
        try:
            pay_hist = Payment.objects.get(tid=tid)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
        
        pay_data = {
            'cid': cid,
            'tid': tid,
            'partner_order_id': pay_hist.partner_order_id,
            'partner_user_id': pay_hist.partner_user_id,
            'pg_token': pg_token
        }
        pay_data = json.dumps(pay_data)
        
        payapprove_url = 'https://kapi.kakaopay.com/v1/payment/approve'
        pay_header = {
            'Authorization': f'KakaoAK {settings.KAKAO_ADMIN_KEY}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

        if response.status_code == 200:
           
            pay_hist.pay_status = 'approved'
            userprofile = UserProfile.objects.get(user=user)
            userprofile.remaining_points += int(pay_hist.point)
            pay_hist.save()
            userprofile.save()

            pay_hist.tid = tid
            pay_hist.save()

        return Response(response.json(), status=response.status_code)
    


class PayHistoryView(APIView):
    def get(self, request):
        print(request)
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Please sign in."}, status=status.HTTP_401_UNAUTHORIZED)

        payments = Payment.objects.filter(user=user)

        if not payments.exists():
            return Response({"detail": "No payment records found."}, status=status.HTTP_404_NOT_FOUND)

        payment_history = []

        for payment in payments:
            tid = payment.tid
            pay_data = {
                'cid': settings.KAKAO_PAY_CID,  # Make sure this is correct
                'tid': tid
            }

            payorder_url = 'https://open-api.kakaopay.com/online/v1/payment/order'
            pay_header = {
                'Authorization': f'SECRET_KEY {settings.KAKAO_ADMIN_KEY}',  # Use the correct secret key format
                'Content-Type': 'application/json',
            }

            try:
                response = requests.post(payorder_url, headers=pay_header, json=pay_data)
                if response.status_code == 200:
                    payment_info = response.json()
                    payment_history.append({
                        'item_name': payment_info['item_name'],
                        'amount': payment_info['amount']['total'],
                        'payment_method_type': payment_info['payment_method_type'],
                        'approved_at': payment_info['approved_at'],
                        'tid': tid
                    })
                else:
                    payment_history.append({
                        'item_name': payment.item_name,
                        'amount': payment.amount,
                        'payment_method_type': 'Unknown',
                        'approved_at': payment.created_at.isoformat(),
                        'tid': tid
                    })
            except requests.exceptions.RequestException as e:
                print(f"Error fetching payment info: {e}")
                payment_history.append({
                    'item_name': payment.item_name,
                    'amount': payment.amount,
                    'payment_method_type': 'Unknown',
                    'approved_at': payment.created_at.isoformat(),
                    'tid': tid
                })

        return Response(payment_history, status=status.HTTP_200_OK)
