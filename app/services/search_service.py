from app.models.product import Product
from sqlalchemy import or_



def search_products(search_text='', sort_by='default'):
    """

    :param search_text: Ieškomas tekstas (produkto pavadinime arba aprašyme)
    :param sort_by: Rikiavimo kriterijus ('price_asc', 'price_desc', 'name_asc', 'name_desc', ir t.t.)
    :return: Produktų sąrašas
    """
    produktai = Product.query

    
    if search_text:
        produktai = produktai.filter(
            or_(
                Product.name.ilike(f'%{search_text}%'),
                Product.description.ilike(f'%{search_text}%')
            )
        )

    # Rikiavimas
    if sort_by == 'price_asc':
        produktai = produktai.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        produktai = produktai.order_by(Product.price.desc())
    elif sort_by == 'name_asc':
        produktai = produktai.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        produktai = produktai.order_by(Product.name.desc())
    elif sort_by == 'best_rated' and hasattr(Product, 'rating'):
        produktai = produktai.order_by(Product.rating.desc())
    elif sort_by == 'most_popular' and hasattr(Product, 'sales_count'):
        produktai = produktai.order_by(Product.sales_count.desc())
    elif sort_by == 'discount':
        produktai = produktai.filter(Product.discount_id.isnot(None)).order_by(Product.price.asc())
    else:
        produktai = produktai.order_by(Product.id)  # default

    return produktai.all()