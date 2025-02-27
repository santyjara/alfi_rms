from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session

from db import get_db
from services import PaymentService
from schemas import PaymentCreate, PaymentResponse

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}},
)

def get_payment_service(db: Session = Depends(get_db)):
    return PaymentService(db)

@router.post("/orders/{order_id}", response_model=PaymentResponse, status_code=201)
def process_payment(
    order_id: int,
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service)
):
    """Process a payment for an order."""
    result = service.process_payment(
        order_id=order_id,
        payment_method=payment.payment_method,
        amount=payment.amount,
        tip_amount=payment.tip_amount
    )
    if not result:
        raise HTTPException(status_code=400, detail="Failed to process payment")
    return result

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """Get a payment by ID."""
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/orders/{order_id}", response_model=List[PaymentResponse])
def get_payments_for_order(
    order_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """Get all payments for a specific order."""
    return service.get_payments_for_order(order_id)