def receipt_to_html(receipt, line_width):
    html_content = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: monospace;
                        white-space: pre-wrap;
                    }}
                    .receipt {{
                        width: {line_width}ch;
                        margin: 0 auto;
                        text-align: left;
                        border: 1px solid #ccc;
                        padding: 5px;
                        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                    }}
                    .center {{
                        text-align: center;
                    }}
                    .line {{
                        border-top: 1px solid #ccc;
                        margin: 2px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="receipt">
                    <div class="center"><strong>{receipt.user.username}</strong></div>
                    <div>{'='*line_width}</div>"""
    for product in receipt.products:
        product_dict = product.to_dict()
        quantity = f"{product_dict['quantity']} x {product_dict['price']}"
        total = f"{product_dict['total']:.2f}"
        html_content += f"""<div>{quantity:<{line_width // 2}}{total:>{line_width // 2}}</div>
                    <div>{product_dict['name']}</div>
                    <div>{'-'*line_width}</div>"""

    html_content += f"""<div class="line"></div>
                    <div>СУМА{' ' * (line_width - 6)}{receipt.total:.2f}</div>
                    <div>{receipt.type}{' ' * (line_width - len(receipt.type) - len(str(receipt.total)))}{receipt.amount:.2f}</div>
                    <div>Решта{' ' * (line_width - 6)}{receipt.rest:.2f}</div>
                    <div class="line"></div>
                    <div class="center">{receipt.created_at.strftime("%d.%m.%Y %H:%M")}</div>
                    <div class="center">Дякуємо за покупку!</div>
                </div>
            </body>
        </html>"""
    return html_content