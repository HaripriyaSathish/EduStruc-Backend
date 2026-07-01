from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import FeeItem, Payment
from .serializers import FeeItemSerializer, PaymentSerializer
import requests
import uuid
from django.conf import settings

from decouple import config
CASHFREE_APP_ID = config('CASHFREE_APP_ID')
CASHFREE_SECRET = config('CASHFREE_SECRET_KEY')
CASHFREE_BASE_URL = 'https://sandbox.cashfree.com/pg'

class FeeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fees = FeeItem.objects.filter(parent=request.user)
        return Response(FeeItemSerializer(fees, many=True).data)

class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        fee_item_ids = request.data.get('fee_item_ids', [])

        if not amount:
            return Response({'error': 'Amount required'}, status=status.HTTP_400_BAD_REQUEST)

        order_id = f"order_{uuid.uuid4().hex[:12]}"

        payload = {
            "order_id": order_id,
            "order_amount": float(amount),
            "order_currency": "INR",
            "customer_details": {
                "customer_id": str(request.user.id),
                "customer_name": request.user.full_name,
                "customer_email": request.user.email,
                "customer_phone": request.user.phone or "9999999999",
            },
            "order_meta": {
                "return_url": f"https://edustruc.com/payment/return?order_id={order_id}",
            }
        }

        headers = {
            "x-api-version": "2023-08-01",
            "x-client-id": CASHFREE_APP_ID,
            "x-client-secret": CASHFREE_SECRET,
            "Content-Type": "application/json",
        }

        try:
            print(f"Creating Cashfree order: {order_id} for amount: {amount}")
            res = requests.post(
                f"{CASHFREE_BASE_URL}/orders",
                json=payload,
                headers=headers,
                timeout=30
            )
            print(f"Cashfree status: {res.status_code}")
            print(f"Cashfree response: {res.text}")

            # Check if response has content
            if not res.text or res.text.strip() == '':
                return Response(
                    {'error': 'Empty response from Cashfree'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            cf_data = res.json()
            print(f"Cashfree data: {cf_data}")

            if res.status_code != 200:
                return Response(
                    {'error': cf_data.get('message', str(cf_data))},
                    status=status.HTTP_400_BAD_REQUEST
                )

            session_id = cf_data.get('payment_session_id', '')
            print(f"RAW SESSION: {repr(session_id)}")


            print(f"CLEAN SESSION: {repr(session_id)}")

            if not session_id:
                  return Response(
        {'error': 'No session ID from Cashfree'},
        status=status.HTTP_400_BAD_REQUEST
    )

            # Save payment record
            payment = Payment.objects.create(
                parent=request.user,
                order_id=order_id,
                cashfree_order_id=cf_data.get('order_id', ''),
                amount=amount,
                status='pending',
            )

            if fee_item_ids:
                payment.fee_items.set(
                    FeeItem.objects.filter(id__in=fee_item_ids)
                )

            print(f"Payment saved. Session ID: {session_id}")

            return Response({
                'order_id': order_id,
                'payment_session_id': session_id,
                'amount': amount,
            })

        except requests.exceptions.Timeout:
            return Response(
                {'error': 'Cashfree request timed out'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'error': 'Cannot connect to Cashfree'},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')

        headers = {
            "x-api-version": "2023-08-01",
            "x-client-id": CASHFREE_APP_ID,
            "x-client-secret": CASHFREE_SECRET,
        }

        try:
            res = requests.get(
                f"{CASHFREE_BASE_URL}/orders/{order_id}",
                headers=headers
            )
            cf_data = res.json()
            cf_status = cf_data.get('order_status', 'PENDING')

            payment = Payment.objects.get(order_id=order_id)

            if cf_status == 'PAID':
                payment.status = 'success'
                payment.save()
                payment.fee_items.update(status='paid')

                # Send receipt email
                try:
                    self.send_receipt_email(payment, request.user)
                except Exception as e:
                    print(f"Email error: {e}")

                return Response({'status': 'success', 'message': 'Payment successful!'})
            elif cf_status == 'FAILED':
                payment.status = 'failed'
                payment.save()
                return Response({'status': 'failed', 'message': 'Payment failed'})
            else:
                return Response({'status': 'pending', 'message': 'Payment pending'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_receipt_email(self, payment, parent):
        from django.core.mail import EmailMessage
        from .receipt import generate_receipt_pdf

        fee_items = payment.fee_items.all()
        pdf_buffer = generate_receipt_pdf(payment, parent, fee_items)

        subject = f'EduParent Payment Receipt — ₹{payment.amount:,.2f}'
        body = f'''
Dear {parent.full_name},

Your payment has been processed successfully! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PAYMENT CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Transaction ID : #{payment.order_id[-8:].upper()}
  Amount Paid   : ₹{payment.amount:,.2f}
  Date          : {payment.created_at.strftime('%B %d, %Y')}
  Status        : ✅ PAID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please find your detailed receipt attached as a PDF.

Thank you for using EduParent!

Best regards,
EduParent Team
EduStruc School Management System
        '''.strip()

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=None,
            to=[parent.email],
        )
        email.attach(
            f'EduParent_Receipt_{payment.order_id[-8:].upper()}.pdf',
            pdf_buffer.read(),
            'application/pdf'
        )
        email.send()
        print(f"Receipt email sent to {parent.email}")

class PaymentHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(parent=request.user)
        return Response(PaymentSerializer(payments, many=True).data)
    
from .models import SavedCard
from .serializers import SavedCardSerializer

class SavedCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cards = SavedCard.objects.filter(parent=request.user)
        return Response(SavedCardSerializer(cards, many=True).data)

    def post(self, request):
        last_four = request.data.get('last_four')
        if not last_four or len(last_four) != 4:
            return Response({'error': 'Invalid card details'}, status=status.HTTP_400_BAD_REQUEST)

        is_first_card = not SavedCard.objects.filter(parent=request.user).exists()

        card = SavedCard.objects.create(
            parent=request.user,
            card_holder_name=request.data.get('card_holder_name', ''),
            last_four=last_four,
            card_type=request.data.get('card_type', 'VISA'),
            expiry_month=request.data.get('expiry_month', ''),
            expiry_year=request.data.get('expiry_year', ''),
            is_default=is_first_card,
        )
        return Response(SavedCardSerializer(card).data, status=status.HTTP_201_CREATED)

class DeleteSavedCardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, card_id):
        try:
            card = SavedCard.objects.get(id=card_id, parent=request.user)
            card.delete()
            return Response({'message': 'Card deleted'})
        except SavedCard.DoesNotExist:
            return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)    