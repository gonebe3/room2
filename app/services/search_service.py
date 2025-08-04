from sqlalchemy import or_
from app.models.product import Product
from app.models.category import Category
from sqlalchemy.exc import SQLAlchemyError





def search_products(search_text='', sort_by='default'):
    """
    Gražina tik aktyvius produktus, atitinkančius paieškos ir rikiavimo kriterijus.

    :param search_text: Ieškomas tekstas produkto pavadinime arba aprašyme.
    :param sort_by: Rikiavimo kriterijus:
        'price_asc', 'price_desc', 'name_asc', 'name_desc',
        'best_rated', 'most_popular', 'discount', arba 'default'.
    :return: Sąrašas aktyvių ir nepašalintų produktų.
    """
    # Pradedame nuo aktyvių produktų
    query = Product.query.filter(
        Product.is_active == True
    )

    # Filtras pagal paieškos tekstą
    if search_text:
        ilike_pattern = f"%{search_text}%"
        query = query.filter(
            or_(
                Product.name.ilike(ilike_pattern),
                Product.description.ilike(ilike_pattern)
            )
        )

    # Rikiavimas pagal pasirinktą kriterijų
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    elif sort_by == 'best_rated' and hasattr(Product, 'rating'):
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'most_popular' and hasattr(Product, 'sales_count'):
        query = query.order_by(Product.sales_count.desc())
    elif sort_by == 'discount':
        # Rikiuojame tuos, kuriems priskirtas discount_id
        query = query.filter(Product.discount_id.isnot(None)).order_by(Product.price.asc())
    else:
        # Numatytoji tvarka pagal įrašų sukūrimo laiką
        query = query.order_by(Product.created_at.desc())

    return query.all()

def filter_products_by_category_id(category_id=None, search_text='', sort_by='default'):
    """
    Filtruoja ir grąžina aktyvius produktus pagal kategorijos id (ar be jo).
    """
    try:
        query = Product.query.filter(Product.is_active == True)

        # Filtras pagal kategorijos id
        if category_id:
            # Patikrinam ar kategorija egzistuoja
            category = Category.query.get(int(category_id))
            if not category:
                return []
            query = query.filter(Product.category_id == category.id)

        # Papildomas tekstinis filtras
        if search_text:
            ilike_pattern = f"%{search_text}%"
            query = query.filter(
                (Product.name.ilike(ilike_pattern)) |
                (Product.description.ilike(ilike_pattern))
            )

        # Rūšiavimas (pagal poreikį)
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'name_asc':
            query = query.order_by(Product.name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(Product.name.desc())
        else:
            query = query.order_by(Product.created_at.desc())

        return query.all()
    except SQLAlchemyError as e:
        print(f"Klaida filtruojant produktus: {e}")
        return []