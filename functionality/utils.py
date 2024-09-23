# utils.py

from decimal import Decimal, ROUND_HALF_UP

def calculate_final_price(base_price, profit_margin=Decimal('0.40'), vat=Decimal('0.09')):
    """
    Calculate the final price by applying a profit margin and VAT.

    :param base_price: The original price of the menu item (Decimal).
    :param profit_margin: The profit margin to apply (default is 40%).
    :param vat: The VAT percentage to apply (default is 9%).
    :return: Final price after applying profit and VAT (Decimal).
    """
    # Ensure base_price is a Decimal
    if not isinstance(base_price, Decimal):
        base_price = Decimal(str(base_price))
    
    price_with_profit = base_price * (Decimal('1') + profit_margin)
    final_price = price_with_profit * (Decimal('1') + vat)
    return final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)