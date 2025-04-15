from inventory_app.models import Inventory


def low_stock_processor(request):
    low_stock_items = Inventory.objects.filter(uniform__minimum_stock_level__isnull=False)
    filtered_items = [i for i in low_stock_items if i.is_low_stock]

    # Serialize needed info for display
    session_items = [
        {'uniform_name': item.uniform.name, 'total_stock': item.total_stock}
        for item in filtered_items
    ]

    request.session['low_stock_items'] = session_items
    request.session['low_stock_count'] = len(session_items)

    return {
        'low_stock_items': session_items,
        'low_stock_count': len(session_items)
    }
