import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape
from db_structs import Order, Product

env = Environment(
    loader=PackageLoader('export_to_pdf'),
    autoescape=select_autoescape()
)

WKHTMLTOPDF_BIN_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_BIN_PATH)

def prepare_order_for_export(order: Order, db_handler) -> dict:
    order_dict = order.dict()
    order_dict['ordered_products'] = []
    for pid, amount in order.ordered_products.items():
        product = Product.read_from_db(db_handler, pid)
        product.amount = amount
        order_dict['ordered_products'].append(product)
    return order_dict

def export_to_pdf(order: dict):
    html = env.get_template('receipt_src.jinja').render(order)
    return pdfkit.from_string(html, configuration=config)

def main():
    order = {
        'name': 'Test',
        'date': 'Yesterday',
        'address': 'Example St.',
        'ordered_products': [
            {
                'name': 'Chair',
                'description': 'Some chair',
                'amount': 23,
                'image_url_list': [
                    'https://via.placeholder.com/200',
                    'https://via.placeholder.com/200'
                ]
            },
            {
                'name': 'Table',
                'description': 'Some table',
                'amount': 1002,
                'image_url_list': [
                    'https://via.placeholder.com/200',
                    'https://via.placeholder.com/200'
                ]
            }
        ]
    }
    with open('test.pdf', 'wb') as f:
        f.write(export_to_pdf(order))

if __name__ == '__main__':
    main()
