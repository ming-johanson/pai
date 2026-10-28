from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_basket_service, require_authenticated_user
from models.schemas import (
    AddBasketItemRequest,
    BasketResponse,
    UpdateBasketItemsRequest,
)
from services.basket_service import BasketService, QuantityLimitError

router = APIRouter(prefix="/api/basket", tags=["basket"])


@router.get("", response_model=BasketResponse)
def get_basket(
    buyer_id: str = Depends(require_authenticated_user),
    service: BasketService = Depends(get_basket_service),
):
    return service.get_or_create_basket(buyer_id)


@router.post("/items", response_model=BasketResponse)
def add_item(
    body: AddBasketItemRequest,
    buyer_id: str = Depends(require_authenticated_user),
    service: BasketService = Depends(get_basket_service),
):
    try:
        return service.add_item(buyer_id, body.catalog_item_id, body.quantity)
    except QuantityLimitError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/items", response_model=BasketResponse)
def update_items(
    body: UpdateBasketItemsRequest,
    buyer_id: str = Depends(require_authenticated_user),
    service: BasketService = Depends(get_basket_service),
):
    try:
        return service.set_quantities(buyer_id, body.quantities)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
