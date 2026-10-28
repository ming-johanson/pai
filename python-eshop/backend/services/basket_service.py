from db.client import DatabaseClient
from models.schemas import MAX_LINE_QUANTITY, BasketItemResponse, BasketResponse


class EmptyBasketError(Exception):
    pass


class QuantityLimitError(Exception):
    pass


class BasketService:
    def __init__(self, db: DatabaseClient):
        self.db = db

    def get_or_create_basket(self, buyer_id: str) -> BasketResponse:
        basket = self.db.get_basket_by_buyer_id(buyer_id)
        if not basket:
            basket = self.db.create_basket(buyer_id)
        return self._to_response(basket)

    def add_item(
        self, buyer_id: str, catalog_item_id: int, quantity: int = 1
    ) -> BasketResponse:
        catalog_item = self.db.get_catalog_item_by_id(catalog_item_id)
        if not catalog_item:
            raise ValueError("Catalog item not found")

        basket = self.db.get_basket_by_buyer_id(buyer_id)
        if not basket:
            basket = self.db.create_basket(buyer_id)

        current = sum(
            item.quantity for item in basket.items if item.catalog_item_id == catalog_item_id
        )
        if current + quantity > MAX_LINE_QUANTITY:
            raise QuantityLimitError(
                f"You can have at most {MAX_LINE_QUANTITY} of an item in your basket"
            )

        self.db.add_basket_item(
            basket.id, catalog_item_id, catalog_item.price, quantity
        )
        updated = self.db.get_basket_by_id(basket.id)
        return self._to_response(updated)

    def set_quantities(self, buyer_id: str, quantities: dict[str, int]) -> BasketResponse:
        basket = self.db.get_basket_by_buyer_id(buyer_id)
        if not basket:
            raise ValueError("Basket not found")

        for item in basket.items:
            if str(item.id) in quantities:
                self.db.update_basket_item_quantity(item.id, quantities[str(item.id)])

        self.db.remove_empty_basket_items(basket.id)
        updated = self.db.get_basket_by_id(basket.id)
        return self._to_response(updated)

    def _to_response(self, basket) -> BasketResponse:
        items = [
            BasketItemResponse(
                id=item.id,
                catalog_item_id=item.catalog_item_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product_name=item.product_name or "",
                picture_uri=item.picture_uri or "",
                line_total=round(item.unit_price * item.quantity, 2),
            )
            for item in basket.items
        ]
        total = round(sum(item.line_total for item in items), 2)
        item_count = sum(item.quantity for item in items)
        return BasketResponse(
            id=basket.id,
            buyer_id=basket.buyer_id,
            items=items,
            total=total,
            item_count=item_count,
        )
