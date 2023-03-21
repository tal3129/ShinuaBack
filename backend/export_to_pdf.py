import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('export_to_pdf'),
    autoescape=select_autoescape()
)

WKHTMLTOPDF_BIN_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_BIN_PATH)

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
