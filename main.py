# MY SHOP - Kivy application
# Preserves the existing home-screen design.
# NEW SALE accepts both product name and product code.
# Includes CASH and M-PESA payment completion.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from datetime import date
import json


class ShopButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(0.12, 0.16, 0.22, 1)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class InfoCard(BoxLayout):
    def __init__(self, title, value, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(4),
            **kwargs
        )
        with self.canvas.before:
            Color(0.12, 0.16, 0.22, 1)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.add_widget(
            Label(
                text=title,
                font_size=dp(13),
                bold=True,
                color=(0.7, 0.75, 0.82, 1)
            )
        )
        self.add_widget(
            Label(
                text=value,
                font_size=dp(22),
                bold=True
            )
        )

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MyShopApp(App):
    PRODUCT_FILE = "myshop_products.json"
    SALES_FILE = "myshop_sales.json"
    CUSTOMER_FILE = "myshop_customers.json"
    EXPENSE_FILE = "myshop_expenses.json"
    SETTINGS_FILE = "myshop_settings.json"

    categories = [
        "Food",
        "Drinks",
        "Household",
        "Clothes",
        "Electronics",
        "Other"
    ]

    def load_file(self, filename, default):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return default

    def save_all(self):
        try:
            files = [
                (self.PRODUCT_FILE, self.products),
                (self.SALES_FILE, self.sales),
                (self.CUSTOMER_FILE, self.customers),
                (self.EXPENSE_FILE, self.expenses),
                (self.SETTINGS_FILE, self.settings),
            ]

            for filename, data in files:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

        except Exception as e:
            print("Save error:", e)

    def money(self, value):
        return f'{self.settings.get("currency", "KSh")} {float(value):,.2f}'

    def new_product_code(self):
        number = 1
        used_codes = {
            str(p.get("code", ""))
            for p in self.products.values()
        }

        while str(number).zfill(3) in used_codes:
            number += 1

        return str(number).zfill(3)

    def find_product(self, search):
        search = str(search).strip().lower()

        # First try exact product name.
        for name in self.products:
            if name.lower() == search:
                return name

        # Then try exact product code.
        for name, product in self.products.items():
            if str(product.get("code", "")).lower() == search:
                return name

        # Finally allow partial name matching.
        matches = [
            name for name in self.products
            if search in name.lower()
        ]

        if len(matches) == 1:
            return matches[0]

        return None

    def next_receipt_number(self):
        numbers = []

        for sale in self.sales:
            try:
                numbers.append(int(sale.get("receipt_number", 0)))
            except (ValueError, TypeError):
                pass

        return str((max(numbers) if numbers else 0) + 1).zfill(6)

    def build(self):
        self.products = self.load_file(
            self.PRODUCT_FILE,
            {
                "Sugar": {
                    "code": "001",
                    "category": "Food",
                    "buying": 120,
                    "selling": 150,
                    "stock": 20
                },
                "Bread": {
                    "code": "002",
                    "category": "Food",
                    "buying": 50,
                    "selling": 70,
                    "stock": 3
                },
                "Soap": {
                    "code": "003",
                    "category": "Household",
                    "buying": 80,
                    "selling": 100,
                    "stock": 45
                }
            }
        )

        self.sales = self.load_file(self.SALES_FILE, [])
        self.customers = self.load_file(self.CUSTOMER_FILE, {})
        self.expenses = self.load_file(self.EXPENSE_FILE, [])
        self.settings = self.load_file(
            self.SETTINGS_FILE,
            {
                "shop_name": "MY SHOP",
                "currency": "KSh"
            }
        )

        self.root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(12)
        )

        self.show_home()
        return self.root

    def label(self, text):
        return Label(
            text=text,
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )

    # ---------------------------------------------------------
    # HOME SCREEN - KEPT IN THE SAME DESIGN
    # ---------------------------------------------------------

    def show_home(self, *args):
        self.root.clear_widgets()

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105)
        )

        header.add_widget(
            Label(
                text=self.settings.get("shop_name", "MY SHOP"),
                font_size=dp(32),
                bold=True
            )
        )

        header.add_widget(
            Label(
                text="SHOP MANAGEMENT",
                font_size=dp(14),
                color=(0.65, 0.7, 0.78, 1)
            )
        )

        self.root.add_widget(header)

        total_stock = sum(
            int(p.get("stock", 0))
            for p in self.products.values()
        )

        today = str(date.today())

        sales_today = sum(
            float(s.get("total", 0))
            for s in self.sales
            if s.get("date") == today
        )

        owing = sum(
            float(c.get("balance", 0))
            for c in self.customers.values()
        )

        currency = self.settings.get("currency", "KSh")

        cards = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(155)
        )

        cards.add_widget(
            InfoCard("PRODUCTS", str(len(self.products)))
        )
        cards.add_widget(
            InfoCard("TOTAL STOCK", str(total_stock))
        )
        cards.add_widget(
            InfoCard("SALES TODAY", f"{currency} {sales_today:.2f}")
        )
        cards.add_widget(
            InfoCard("CUSTOMERS OWING", f"{currency} {owing:.2f}")
        )

        self.root.add_widget(cards)

        self.root.add_widget(
            Label(
                text="SHOP MENU",
                font_size=dp(19),
                bold=True,
                size_hint_y=None,
                height=dp(45)
            )
        )

        menu = GridLayout(
            cols=2,
            spacing=dp(10)
        )

        menu.add_widget(
            self.make_button("DASHBOARD", self.show_dashboard)
        )
        menu.add_widget(
            self.make_button("ADD PRODUCT", self.show_add_product)
        )
        menu.add_widget(
            self.make_button("PRODUCTS", self.show_products)
        )
        menu.add_widget(
            self.make_button("NEW SALE", self.show_new_sale)
        )
        menu.add_widget(
            self.make_button("PAY LATER", self.show_credit_sale)
        )
        menu.add_widget(
            self.make_button("CUSTOMERS", self.show_customers)
        )
        menu.add_widget(
            self.make_button("REPORTS", self.show_reports)
        )
        menu.add_widget(
            self.make_button("SETTINGS", self.show_settings)
        )

        self.root.add_widget(menu)

    def make_button(self, text, function):
        button = ShopButton(
            text=text,
            font_size=dp(16),
            bold=True
        )
        button.bind(on_press=function)
        return button

    def page(self, title):
        self.root.clear_widgets()

        self.root.add_widget(
            Label(
                text=title,
                font_size=dp(28),
                bold=True,
                size_hint_y=None,
                height=dp(60)
            )
        )

    def back_button(self):
        button = ShopButton(
            text="BACK TO HOME",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(55)
        )
        button.bind(on_press=self.show_home)
        return button

    def scroll_area(self):
        scroll = ScrollView()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(5),
            size_hint_y=None
        )

        content.bind(
            minimum_height=content.setter("height")
        )

        scroll.add_widget(content)

        return scroll, content

    def popup(self, title, message):
        box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        box.add_widget(
            Label(
                text=message,
                font_size=dp(17)
            )
        )

        close = ShopButton(
            text="OK",
            size_hint_y=None,
            height=dp(50)
        )

        box.add_widget(close)

        pop = Popup(
            title=title,
            content=box,
            size_hint=(0.9, 0.45)
        )

        close.bind(on_press=pop.dismiss)
        pop.open()

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------

    def show_dashboard(self, instance=None):
        self.page("DASHBOARD")

        today = str(date.today())

        total_stock = sum(
            int(p.get("stock", 0))
            for p in self.products.values()
        )

        low = sum(
            1
            for p in self.products.values()
            if int(p.get("stock", 0)) <= 5
        )

        sales_today = [
            s for s in self.sales
            if s.get("date") == today
        ]

        total_sales = sum(
            float(s.get("total", 0))
            for s in sales_today
        )

        profit = sum(
            float(s.get("profit", 0))
            for s in sales_today
        )

        expenses = sum(
            float(e.get("amount", 0))
            for e in self.expenses
            if e.get("date") == today
        )

        debt = sum(
            float(c.get("balance", 0))
            for c in self.customers.values()
        )

        currency = self.settings.get("currency", "KSh")

        scroll, content = self.scroll_area()

        data = [
            ("PRODUCTS", len(self.products)),
            ("TOTAL STOCK", total_stock),
            ("LOW STOCK PRODUCTS", low),
            ("TODAY'S SALES", f"{currency} {total_sales:.2f}"),
            ("TODAY'S PROFIT", f"{currency} {profit:.2f}"),
            ("TODAY'S EXPENSES", f"{currency} {expenses:.2f}"),
            ("TODAY'S NET PROFIT", f"{currency} {profit-expenses:.2f}"),
            (
                "CUSTOMERS OWING",
                sum(
                    1
                    for c in self.customers.values()
                    if float(c.get("balance", 0)) > 0
                )
            ),
            ("TOTAL MONEY OWED", f"{currency} {debt:.2f}")
        ]

        for title, value in data:
            content.add_widget(
                Label(
                    text=f"{title}:  {value}",
                    font_size=dp(19),
                    size_hint_y=None,
                    height=dp(48)
                )
            )

        self.root.add_widget(scroll)
        self.root.add_widget(self.back_button())

    # ---------------------------------------------------------
    # ADD PRODUCT
    # ---------------------------------------------------------

    def show_add_product(self, instance=None):
        self.page("ADD PRODUCT")

        scroll, content = self.scroll_area()

        self.product_name_input = TextInput(
            hint_text="Product name",
            multiline=False,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(self.product_name_input)

        content.add_widget(
            Label(
                text="SELECT CATEGORY",
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(40)
            )
        )

        self.category_buttons = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180)
        )

        self.selected_category = ""

        self.category_label = Label(
            text="Category: Not selected",
            font_size=dp(17),
            size_hint_y=None,
            height=dp(40)
        )

        for category in self.categories:
            b = ShopButton(
                text=category,
                font_size=dp(16),
                size_hint_y=None,
                height=dp(50)
            )
            b.bind(on_press=self.select_category)
            self.category_buttons.add_widget(b)

        content.add_widget(self.category_buttons)
        content.add_widget(self.category_label)

        self.buying_input = TextInput(
            hint_text="Buying price (KSh)",
            multiline=False,
            input_filter="float",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        self.selling_input = TextInput(
            hint_text="Selling price (KSh)",
            multiline=False,
            input_filter="float",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        self.stock_input = TextInput(
            hint_text="Starting stock",
            multiline=False,
            input_filter="int",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(self.buying_input)
        content.add_widget(self.selling_input)
        content.add_widget(self.stock_input)

        save = ShopButton(
            text="SAVE PRODUCT",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(58)
        )

        save.bind(on_press=self.save_product)
        content.add_widget(save)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    def select_category(self, instance):
        self.selected_category = instance.text
        self.category_label.text = "Category: " + instance.text

    def save_product(self, instance):
        name = self.product_name_input.text.strip()

        if not name:
            self.popup(
                "Missing information",
                "Enter a product name."
            )
            return

        duplicate = next(
            (
                existing
                for existing in self.products
                if existing.lower() == name.lower()
            ),
            None
        )

        if duplicate:
            self.popup(
                "Product exists",
                "That product already exists."
            )
            return

        if not self.selected_category:
            self.popup(
                "Category",
                "Please select a category."
            )
            return

        try:
            buying = float(self.buying_input.text)
            selling = float(self.selling_input.text)
            stock = int(self.stock_input.text)
        except ValueError:
            self.popup(
                "Invalid input",
                "Enter valid prices and stock."
            )
            return

        if buying < 0 or selling < 0 or stock < 0:
            self.popup(
                "Invalid input",
                "Values cannot be negative."
            )
            return

        code = self.new_product_code()

        self.products[name] = {
            "code": code,
            "category": self.selected_category,
            "buying": buying,
            "selling": selling,
            "stock": stock
        }

        self.save_all()

        self.popup(
            "Product saved",
            f"Product saved successfully!\n\n"
            f"Product: {name}\n"
            f"Product Code: {code}"
        )

        self.show_add_product()

    # ---------------------------------------------------------
    # PRODUCTS
    # ---------------------------------------------------------

    def show_products(self, instance=None):
        self.page("PRODUCTS")

        scroll, content = self.scroll_area()

        if not self.products:
            content.add_widget(
                Label(
                    text="No products yet.",
                    font_size=dp(18),
                    size_hint_y=None,
                    height=dp(50)
                )
            )

        else:
            for name, p in self.products.items():
                code = p.get("code", "N/A")
                category = p.get("category", "Other")
                buying = float(p.get("buying", 0))
                selling = float(p.get("selling", 0))
                stock = int(p.get("stock", 0))

                warning = (
                    "\n⚠️ LOW STOCK"
                    if stock <= 5
                    else ""
                )

                text = (
                    f"PRODUCT CODE: {code}\n"
                    f"PRODUCT: {name}\n"
                    f"CATEGORY: {category}\n"
                    f"BUYING: {self.money(buying)}\n"
                    f"SELLING: {self.money(selling)}\n"
                    f"STOCK: {stock}{warning}"
                )

                content.add_widget(
                    Label(
                        text=text,
                        font_size=dp(16),
                        size_hint_y=None,
                        height=dp(145)
                    )
                )

        self.root.add_widget(scroll)
        self.root.add_widget(self.back_button())

    # ---------------------------------------------------------
    # NEW SALE
    # ---------------------------------------------------------

    def show_new_sale(self, instance=None):
        self.page("NEW SALE")

        self.cart = []

        scroll, content = self.scroll_area()

        self.sale_product_input = TextInput(
            hint_text="Product name or code",
            multiline=False,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        self.sale_quantity_input = TextInput(
            hint_text="Quantity",
            multiline=False,
            input_filter="int",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(self.sale_product_input)
        content.add_widget(self.sale_quantity_input)

        add = ShopButton(
            text="ADD TO CART",
            size_hint_y=None,
            height=dp(55)
        )

        add.bind(on_press=self.add_to_cart)
        content.add_widget(add)

        edit = ShopButton(
            text="EDIT CART",
            size_hint_y=None,
            height=dp(55)
        )

        edit.bind(on_press=self.show_edit_cart)
        content.add_widget(edit)

        self.cart_label = Label(
            text="Cart is empty.",
            font_size=dp(17),
            size_hint_y=None,
            height=dp(130)
        )

        content.add_widget(self.cart_label)

        self.total_label = Label(
            text=f"TOTAL: {self.money(0)}",
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(55)
        )

        content.add_widget(self.total_label)

        payment = ShopButton(
            text="CONTINUE TO PAYMENT",
            font_size=dp(17),
            size_hint_y=None,
            height=dp(58)
        )

        payment.bind(on_press=self.show_payment)
        content.add_widget(payment)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    def add_to_cart(self, instance):
        search = self.sale_product_input.text.strip()
        qty_text = self.sale_quantity_input.text.strip()

        if not search:
            self.popup(
                "Product",
                "Enter a product name or product code."
            )
            return

        actual = self.find_product(search)

        if not actual:
            self.popup(
                "Product",
                "Product not found.\n\n"
                "Enter the exact product name or product code."
            )
            return

        try:
            qty = int(qty_text)
        except ValueError:
            self.popup(
                "Quantity",
                "Enter a valid quantity."
            )
            return

        if qty <= 0:
            self.popup(
                "Quantity",
                "Quantity must be greater than zero."
            )
            return

        p = self.products[actual]

        already = sum(
            i["quantity"]
            for i in self.cart
            if i["product"] == actual
        )

        available = int(p.get("stock", 0)) - already

        if qty > available:
            self.popup(
                "Stock",
                f"Available stock: {available}"
            )
            return

        price = float(p.get("selling", 0))
        buying = float(p.get("buying", 0))

        self.cart.append({
            "product": actual,
            "quantity": qty,
            "price": price,
            "total": qty * price,
            "profit": qty * (price - buying)
        })

        self.sale_product_input.text = ""
        self.sale_quantity_input.text = ""

        self.update_cart()

    def update_cart(self):
        if not self.cart:
            self.cart_label.text = "Cart is empty."
            self.total_label.text = f"TOTAL: {self.money(0)}"
            return

        total = sum(
            float(i["total"])
            for i in self.cart
        )

        self.cart_label.text = "\n".join(
            f"{i}. {x['product']} x {x['quantity']} = "
            f"{self.money(x['total'])}"
            for i, x in enumerate(self.cart, 1)
        )

        self.total_label.text = (
            f"TOTAL: {self.money(total)}"
        )

    def show_edit_cart(self, instance=None):
        if not self.cart:
            self.popup(
                "Cart",
                "The cart is empty."
            )
            return

        self.page("EDIT CART")

        scroll, content = self.scroll_area()

        for index, item in enumerate(self.cart, 1):
            content.add_widget(
                Label(
                    text=(
                        f"{index}. {item['product']} x "
                        f"{item['quantity']} = "
                        f"{self.money(item['total'])}"
                    ),
                    font_size=dp(17),
                    size_hint_y=None,
                    height=dp(45)
                )
            )

        item_number = TextInput(
            hint_text="Item number",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(52)
        )

        new_quantity = TextInput(
            hint_text="New quantity",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(item_number)
        content.add_widget(new_quantity)

        update = ShopButton(
            text="UPDATE QUANTITY",
            size_hint_y=None,
            height=dp(55)
        )

        def update_item(_):
            try:
                number = int(item_number.text)
                qty = int(new_quantity.text)
            except ValueError:
                self.popup(
                    "Cart",
                    "Enter valid item number and quantity."
                )
                return

            if not 1 <= number <= len(self.cart):
                self.popup(
                    "Cart",
                    "Invalid item number."
                )
                return

            if qty <= 0:
                self.popup(
                    "Cart",
                    "Quantity must be greater than zero."
                )
                return

            item = self.cart[number - 1]
            product = self.products[item["product"]]

            other_quantity = sum(
                x["quantity"]
                for i, x in enumerate(self.cart)
                if i != number - 1
                and x["product"] == item["product"]
            )

            available = (
                int(product.get("stock", 0))
                - other_quantity
            )

            if qty > available:
                self.popup(
                    "Stock",
                    f"Available stock: {available}"
                )
                return

            item["quantity"] = qty
            item["total"] = qty * item["price"]
            item["profit"] = qty * (
                item["price"]
                - float(product.get("buying", 0))
            )

            self.show_new_sale()

        update.bind(on_press=update_item)
        content.add_widget(update)

        remove = ShopButton(
            text="REMOVE ITEM",
            size_hint_y=None,
            height=dp(55)
        )

        def remove_item(_):
            try:
                number = int(item_number.text)
            except ValueError:
                self.popup(
                    "Cart",
                    "Enter the item number."
                )
                return

            if not 1 <= number <= len(self.cart):
                self.popup(
                    "Cart",
                    "Invalid item number."
                )
                return

            self.cart.pop(number - 1)
            self.show_new_sale()

        remove.bind(on_press=remove_item)
        content.add_widget(remove)

        back = ShopButton(
            text="BACK TO SALE",
            size_hint_y=None,
            height=dp(55)
        )
        back.bind(on_press=self.show_new_sale)
        content.add_widget(back)

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # PAYMENT
    # ---------------------------------------------------------

    def show_payment(self, instance=None):
        if not self.cart:
            self.popup(
                "Sale",
                "Add at least one product to the cart."
            )
            return

        self.page("PAYMENT")

        scroll, content = self.scroll_area()

        total = sum(
            float(item["total"])
            for item in self.cart
        )

        content.add_widget(
            Label(
                text=f"TOTAL: {self.money(total)}",
                font_size=dp(24),
                bold=True,
                size_hint_y=None,
                height=dp(60)
            )
        )

        cash_button = ShopButton(
            text="CASH",
            size_hint_y=None,
            height=dp(60)
        )

        cash_button.bind(
            on_press=lambda x: self.show_cash_payment(total)
        )

        content.add_widget(cash_button)

        mpesa_button = ShopButton(
            text="M-PESA",
            size_hint_y=None,
            height=dp(60)
        )

        mpesa_button.bind(
            on_press=lambda x: self.show_mpesa_payment(total)
        )

        content.add_widget(mpesa_button)

        back = ShopButton(
            text="BACK TO CART",
            size_hint_y=None,
            height=dp(55)
        )

        back.bind(on_press=self.show_new_sale)
        content.add_widget(back)

        self.root.add_widget(scroll)

    def show_cash_payment(self, total):
        self.page("CASH PAYMENT")

        scroll, content = self.scroll_area()

        content.add_widget(
            Label(
                text=f"TOTAL: {self.money(total)}",
                font_size=dp(23),
                bold=True,
                size_hint_y=None,
                height=dp(55)
            )
        )

        cash = TextInput(
            hint_text="Cash received",
            multiline=False,
            input_filter="float",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(cash)

        complete = ShopButton(
            text="COMPLETE CASH SALE",
            size_hint_y=None,
            height=dp(58)
        )

        def complete_cash(_):
            try:
                received = float(cash.text)
            except ValueError:
                self.popup(
                    "Cash",
                    "Enter a valid cash amount."
                )
                return

            if received < total:
                self.popup(
                    "Cash",
                    f"Not enough cash.\nRequired: {self.money(total)}"
                )
                return

            change = received - total
            self.complete_sale(
                "CASH",
                cash_received=received,
                change=change
            )

        complete.bind(on_press=complete_cash)
        content.add_widget(complete)

        back = ShopButton(
            text="BACK TO PAYMENT",
            size_hint_y=None,
            height=dp(55)
        )
        back.bind(on_press=lambda x: self.show_payment())
        content.add_widget(back)

        self.root.add_widget(scroll)

    def show_mpesa_payment(self, total):
        self.page("M-PESA PAYMENT")

        scroll, content = self.scroll_area()

        content.add_widget(
            Label(
                text=f"TOTAL: {self.money(total)}",
                font_size=dp(23),
                bold=True,
                size_hint_y=None,
                height=dp(55)
            )
        )

        reference = TextInput(
            hint_text="M-Pesa transaction code",
            multiline=False,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(reference)

        complete = ShopButton(
            text="COMPLETE M-PESA SALE",
            size_hint_y=None,
            height=dp(58)
        )

        def complete_mpesa(_):
            ref = reference.text.strip().upper()

            if not ref:
                self.popup(
                    "M-Pesa",
                    "Enter the M-Pesa transaction code."
                )
                return

            self.complete_sale(
                "M-PESA",
                reference=ref
            )

        complete.bind(on_press=complete_mpesa)
        content.add_widget(complete)

        back = ShopButton(
            text="BACK TO PAYMENT",
            size_hint_y=None,
            height=dp(55)
        )
        back.bind(on_press=lambda x: self.show_payment())
        content.add_widget(back)

        self.root.add_widget(scroll)

    def complete_sale(
        self,
        payment,
        cash_received=0,
        change=0,
        reference=""
    ):
        total = sum(
            float(item["total"])
            for item in self.cart
        )

        profit = sum(
            float(item["profit"])
            for item in self.cart
        )

        # Confirm stock before changing anything.
        for item in self.cart:
            product = self.products.get(item["product"])

            if product is None:
                self.popup(
                    "Sale",
                    f"Product not found: {item['product']}"
                )
                return

            if int(product.get("stock", 0)) < int(item["quantity"]):
                self.popup(
                    "Stock",
                    f"Not enough stock for {item['product']}."
                )
                return

        receipt_number = self.next_receipt_number()

        for item in self.cart:
            self.products[item["product"]]["stock"] -= int(
                item["quantity"]
            )

        sale = {
            "receipt_number": receipt_number,
            "date": str(date.today()),
            "items": self.cart.copy(),
            "total": total,
            "profit": profit,
            "payment": payment,
            "customer": "",
            "phone": "",
            "reference": reference
        }

        if payment == "CASH":
            sale["cash_received"] = cash_received
            sale["change"] = change

        self.sales.append(sale)
        self.save_all()

        # Show a professional receipt-style popup.
        self.show_sales_receipt(
            receipt_number=receipt_number,
            payment=payment,
            cash_received=cash_received,
            change=change,
            reference=reference,
            total=total
        )

        self.cart = []

    def show_sales_receipt(
        self,
        receipt_number,
        payment,
        cash_received=0,
        change=0,
        reference="",
        total=0
    ):
        """Display a clean, phone-friendly shop receipt."""

        # Outer receipt layout
        receipt = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8)
        )

        # Receipt header
        shop_name = self.settings.get("shop_name", "MY SHOP")
        currency = self.settings.get("currency", "KSh")

        receipt.add_widget(
            Label(
                text=shop_name,
                font_size=dp(25),
                bold=True,
                size_hint_y=None,
                height=dp(38)
            )
        )

        receipt.add_widget(
            Label(
                text="SALES RECEIPT",
                font_size=dp(16),
                bold=True,
                size_hint_y=None,
                height=dp(28)
            )
        )

        receipt.add_widget(
            Label(
                text=f"Receipt No: {receipt_number}    Date: {date.today()}",
                font_size=dp(13),
                size_hint_y=None,
                height=dp(30)
            )
        )

        # Separator
        receipt.add_widget(
            Label(
                text="━━━━━━━━━━━━━━━━━━━━━━━━",
                font_size=dp(12),
                size_hint_y=None,
                height=dp(22)
            )
        )

        # Column headings
        headings = GridLayout(
            cols=4,
            spacing=dp(3),
            size_hint_y=None,
            height=dp(30)
        )

        for heading in ("ITEM", "QTY", "PRICE", "TOTAL"):
            headings.add_widget(
                Label(
                    text=heading,
                    font_size=dp(12),
                    bold=True
                )
            )

        receipt.add_widget(headings)

        # Items
        items_scroll = ScrollView(
            size_hint_y=1
        )

        items = GridLayout(
            cols=4,
            spacing=dp(3),
            size_hint_y=None,
            padding=(0, dp(3), 0, dp(3))
        )
        items.bind(minimum_height=items.setter("height"))

        for item in self.cart:
            name = str(item.get("product", ""))
            qty = str(item.get("quantity", 0))
            price = self.money(item.get("price", 0))
            item_total = self.money(item.get("total", 0))

            # Keep long names readable on small phone screens.
            if len(name) > 18:
                name = name[:17] + "…"

            values = (name, qty, price, item_total)

            for value in values:
                items.add_widget(
                    Label(
                        text=value,
                        font_size=dp(12),
                        halign="center",
                        valign="middle",
                        text_size=(None, None)
                    )
                )

        items_scroll.add_widget(items)
        receipt.add_widget(items_scroll)

        # Total section
        receipt.add_widget(
            Label(
                text="━━━━━━━━━━━━━━━━━━━━━━━━",
                font_size=dp(12),
                size_hint_y=None,
                height=dp(22)
            )
        )

        receipt.add_widget(
            Label(
                text=f"TOTAL   {self.money(total)}",
                font_size=dp(21),
                bold=True,
                size_hint_y=None,
                height=dp(38)
            )
        )

        receipt.add_widget(
            Label(
                text=f"PAYMENT: {payment}",
                font_size=dp(14),
                bold=True,
                size_hint_y=None,
                height=dp(28)
            )
        )

        if payment == "CASH":
            receipt.add_widget(
                Label(
                    text=f"Cash Received: {self.money(cash_received)}",
                    font_size=dp(13),
                    size_hint_y=None,
                    height=dp(26)
                )
            )
            receipt.add_widget(
                Label(
                    text=f"Change: {self.money(change)}",
                    font_size=dp(15),
                    bold=True,
                    size_hint_y=None,
                    height=dp(28)
                )
            )

        elif payment == "M-PESA":
            receipt.add_widget(
                Label(
                    text=f"M-Pesa Reference: {reference}",
                    font_size=dp(13),
                    size_hint_y=None,
                    height=dp(28)
                )
            )

        receipt.add_widget(
            Label(
                text="━━━━━━━━━━━━━━━━━━━━━━━━",
                font_size=dp(12),
                size_hint_y=None,
                height=dp(22)
            )
        )

        receipt.add_widget(
            Label(
                text="THANK YOU FOR SHOPPING!",
                font_size=dp(15),
                bold=True,
                size_hint_y=None,
                height=dp(32)
            )
        )

        close = ShopButton(
            text="CLOSE RECEIPT",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(52)
        )
        receipt.add_widget(close)

        pop = Popup(
            title="SALE COMPLETE",
            content=receipt,
            size_hint=(0.96, 0.88),
            auto_dismiss=False
        )

        close.bind(
            on_press=lambda instance: (
                pop.dismiss(),
                self.show_home()
            )
        )

        pop.open()

    # ---------------------------------------------------------
    # REPORTS
    # ---------------------------------------------------------

    def show_reports(self, instance=None):
        self.page("REPORTS")

        menu = GridLayout(
            cols=2,
            spacing=dp(10)
        )

        menu.add_widget(
            self.make_button(
                "TODAY'S REPORT",
                self.today_report
            )
        )

        menu.add_widget(
            self.make_button(
                "STOCK VALUE",
                self.stock_value_report
            )
        )

        menu.add_widget(
            self.make_button(
                "ADD EXPENSE",
                self.show_expense
            )
        )

        menu.add_widget(
            self.make_button(
                "ADD STOCK",
                self.add_stock
            )
        )

        menu.add_widget(
            self.make_button(
                "EDIT PRODUCT",
                self.edit_product
            )
        )

        menu.add_widget(
            self.make_button(
                "DELETE PRODUCT",
                self.delete_product
            )
        )

        menu.add_widget(self.back_button())

        self.root.add_widget(menu)

    def report_page(self, title, lines):
        self.page(title)

        scroll, content = self.scroll_area()

        for line in lines:
            content.add_widget(
                Label(
                    text=line,
                    font_size=dp(17),
                    size_hint_y=None,
                    height=dp(45)
                )
            )

        self.root.add_widget(scroll)
        self.root.add_widget(self.back_button())

    def today_report(self, instance=None):
        t = str(date.today())

        s = [
            x for x in self.sales
            if x.get("date") == t
        ]

        total = sum(
            float(x.get("total", 0))
            for x in s
        )

        profit = sum(
            float(x.get("profit", 0))
            for x in s
        )

        exp = sum(
            float(x.get("amount", 0))
            for x in self.expenses
            if x.get("date") == t
        )

        c = self.settings.get("currency", "KSh")

        self.report_page(
            "TODAY'S REPORT",
            [
                f"Date: {t}",
                f"Total sales: {c} {total:.2f}",
                f"Gross profit: {c} {profit:.2f}",
                f"Expenses: {c} {exp:.2f}",
                f"NET PROFIT: {c} {profit-exp:.2f}",
                f"Number of sales: {len(s)}"
            ]
        )

    def stock_value_report(self, instance=None):
        buy = sum(
            float(p.get("buying", 0))
            * int(p.get("stock", 0))
            for p in self.products.values()
        )

        sell = sum(
            float(p.get("selling", 0))
            * int(p.get("stock", 0))
            for p in self.products.values()
        )

        c = self.settings.get("currency", "KSh")

        self.report_page(
            "STOCK VALUE REPORT",
            [
                f"Products: {len(self.products)}",
                f"Buying value: {c} {buy:.2f}",
                f"Selling value: {c} {sell:.2f}",
                f"Potential profit: {c} {sell-buy:.2f}"
            ]
        )

    # ---------------------------------------------------------
    # EXPENSES
    # ---------------------------------------------------------

    def show_expense(self, instance=None):
        self.page("ADD EXPENSE")

        scroll, content = self.scroll_area()

        desc = TextInput(
            hint_text="Expense description",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        amount = TextInput(
            hint_text="Amount (KSh)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(desc)
        content.add_widget(amount)

        btn = ShopButton(
            text="SAVE EXPENSE",
            size_hint_y=None,
            height=dp(58)
        )

        def save(_):
            try:
                a = float(amount.text)
            except ValueError:
                self.popup(
                    "Expense",
                    "Enter a valid amount."
                )
                return

            if not desc.text.strip() or a <= 0:
                self.popup(
                    "Expense",
                    "Enter a description and valid amount."
                )
                return

            self.expenses.append({
                "date": str(date.today()),
                "description": desc.text.strip(),
                "amount": a
            })

            self.save_all()

            self.popup(
                "Expense saved",
                f"{self.money(a)} saved."
            )

            self.show_home()

        btn.bind(on_press=save)
        content.add_widget(btn)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # ADD STOCK
    # ---------------------------------------------------------

    def add_stock(self, instance=None):
        self.page("ADD STOCK")

        scroll, content = self.scroll_area()

        name = TextInput(
            hint_text="Product name or code",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        qty = TextInput(
            hint_text="Quantity",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(name)
        content.add_widget(qty)

        btn = ShopButton(
            text="ADD STOCK",
            size_hint_y=None,
            height=dp(55)
        )

        def add(_):
            actual = self.find_product(name.text.strip())

            try:
                q = int(qty.text)
            except ValueError:
                self.popup(
                    "Stock",
                    "Enter a valid quantity."
                )
                return

            if not actual or q <= 0:
                self.popup(
                    "Stock",
                    "Check product and quantity."
                )
                return

            self.products[actual]["stock"] += q
            self.save_all()

            self.popup(
                "Stock updated",
                f"New stock: {self.products[actual]['stock']}"
            )

            self.show_home()

        btn.bind(on_press=add)
        content.add_widget(btn)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # EDIT PRODUCT
    # ---------------------------------------------------------

    def edit_product(self, instance=None):
        self.page("EDIT PRODUCT")

        scroll, content = self.scroll_area()

        old = TextInput(
            hint_text="Existing product name or code",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        buy = TextInput(
            hint_text="New buying price",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(52)
        )

        sell = TextInput(
            hint_text="New selling price",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(52)
        )

        stock = TextInput(
            hint_text="New stock",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(52)
        )

        new = TextInput(
            hint_text="New name (optional)",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        for w in [old, new, buy, sell, stock]:
            content.add_widget(w)

        btn = ShopButton(
            text="UPDATE PRODUCT",
            size_hint_y=None,
            height=dp(55)
        )

        def edit(_):
            actual = self.find_product(old.text.strip())

            if not actual:
                self.popup(
                    "Product",
                    "Product not found."
                )
                return

            p = self.products[actual]

            try:
                if buy.text.strip():
                    p["buying"] = float(buy.text)

                if sell.text.strip():
                    p["selling"] = float(sell.text)

                if stock.text.strip():
                    p["stock"] = int(stock.text)

            except ValueError:
                self.popup(
                    "Product",
                    "Invalid number."
                )
                return

            if (
                float(p.get("buying", 0)) < 0
                or float(p.get("selling", 0)) < 0
                or int(p.get("stock", 0)) < 0
            ):
                self.popup(
                    "Product",
                    "Values cannot be negative."
                )
                return

            target = new.text.strip()

            if target and target.lower() != actual.lower():
                duplicate = next(
                    (
                        n for n in self.products
                        if n.lower() == target.lower()
                    ),
                    None
                )

                if duplicate:
                    self.popup(
                        "Product",
                        "New name already exists."
                    )
                    return

                self.products[target] = p
                del self.products[actual]

            self.save_all()

            self.popup(
                "Updated",
                "Product updated successfully."
            )

            self.show_home()

        btn.bind(on_press=edit)
        content.add_widget(btn)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # DELETE PRODUCT
    # ---------------------------------------------------------

    def delete_product(self, instance=None):
        self.page("DELETE PRODUCT")

        box = BoxLayout(
            orientation="vertical",
            spacing=dp(10)
        )

        name = TextInput(
            hint_text="Product name or code",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        btn = ShopButton(
            text="DELETE PRODUCT",
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(name)
        box.add_widget(btn)
        box.add_widget(self.back_button())

        def delete(_):
            actual = self.find_product(name.text.strip())

            if not actual:
                self.popup(
                    "Delete",
                    "Product not found."
                )
                return

            del self.products[actual]
            self.save_all()

            self.popup(
                "Deleted",
                f"{actual} deleted."
            )

            self.show_home()

        btn.bind(on_press=delete)

        self.root.add_widget(box)

    # ---------------------------------------------------------
    # CUSTOMERS
    # ---------------------------------------------------------

    def show_customers(self, instance=None):
        self.page("CUSTOMERS / DEBTS")

        # Keep the customer list scrollable, but keep the action buttons
        # fixed at the bottom so they never move down as customers increase.
        scroll, content = self.scroll_area()

        if not self.customers:
            content.add_widget(
                Label(
                    text="No customers yet.",
                    size_hint_y=None,
                    height=dp(50)
                )
            )

        else:
            found = False

            for phone, c in self.customers.items():
                b = float(c.get("balance", 0))

                if b > 0:
                    found = True

                    content.add_widget(
                        Label(
                            text=(
                                f"{c.get('name', '')} | {phone}\n"
                                f"OWES: {self.money(b)}"
                            ),
                            size_hint_y=None,
                            height=dp(65)
                        )
                    )

            if not found:
                content.add_widget(
                    Label(
                        text="Nobody currently owes money.",
                        size_hint_y=None,
                        height=dp(50)
                    )
                )

        self.root.add_widget(scroll)

        # FIXED CUSTOMER ACTION BAR
        # These buttons stay visible at the bottom regardless of the
        # number of customers in the scrollable list.
        actions = BoxLayout(
            orientation="horizontal",
            spacing=dp(7),
            padding=(0, dp(7), 0, 0),
            size_hint_y=None,
            height=dp(62)
        )

        payment = ShopButton(
            text="CUSTOMER\nPAYMENT",
            font_size=dp(12),
            bold=True
        )
        payment.bind(on_press=self.customer_payment)

        history = ShopButton(
            text="CUSTOMER\nHISTORY",
            font_size=dp(12),
            bold=True
        )
        history.bind(on_press=self.customer_history)

        back = ShopButton(
            text="BACK\nTO HOME",
            font_size=dp(12),
            bold=True
        )
        back.bind(on_press=self.show_home)

        actions.add_widget(payment)
        actions.add_widget(history)
        actions.add_widget(back)

        self.root.add_widget(actions)

    # ---------------------------------------------------------
    # CREDIT / PAY LATER
    # ---------------------------------------------------------

    def show_credit_sale(self, instance=None):
        self.page("PAY LATER / CREDIT SALE")

        scroll, content = self.scroll_area()

        content.add_widget(self.label("Customer Name"))

        customer_name = TextInput(
            hint_text="Enter customer name",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(customer_name)

        content.add_widget(self.label("Customer Phone"))

        phone = TextInput(
            hint_text="Enter phone number",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(phone)

        content.add_widget(self.label("Product"))

        product_name = TextInput(
            hint_text="Enter product name or code",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(product_name)

        content.add_widget(self.label("Quantity"))

        quantity = TextInput(
            hint_text="Enter quantity",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(quantity)

        content.add_widget(self.label("Payment Due Date"))

        due_date = TextInput(
            hint_text="YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(due_date)

        save_button = ShopButton(
            text="SAVE CREDIT SALE",
            size_hint_y=None,
            height=dp(55)
        )

        def save_credit(instance):
            name = customer_name.text.strip()
            customer_phone = phone.text.strip()
            product = product_name.text.strip()
            qty_text = quantity.text.strip()
            due = due_date.text.strip()

            if not name:
                self.popup(
                    "Error",
                    "Please enter customer name."
                )
                return

            if not customer_phone:
                self.popup(
                    "Error",
                    "Please enter customer phone."
                )
                return

            if not product:
                self.popup(
                    "Error",
                    "Please enter product name or code."
                )
                return

            try:
                qty = int(qty_text)

                if qty <= 0:
                    raise ValueError

            except ValueError:
                self.popup(
                    "Error",
                    "Enter a valid quantity."
                )
                return

            if not due:
                self.popup(
                    "Error",
                    "Please enter payment due date."
                )
                return

            try:
                date.fromisoformat(due)
            except ValueError:
                self.popup(
                    "Error",
                    "Use due date format YYYY-MM-DD."
                )
                return

            product_key = self.find_product(product)

            if product_key is None:
                self.popup(
                    "Error",
                    "Product not found."
                )
                return

            pdata = self.products[product_key]

            if int(pdata.get("stock", 0)) < qty:
                self.popup(
                    "Not Enough Stock",
                    f"Available stock: {pdata.get('stock', 0)}"
                )
                return

            price = float(pdata.get("selling", 0))
            buying = float(pdata.get("buying", 0))

            total = price * qty
            profit = (price - buying) * qty

            if customer_phone not in self.customers:
                self.customers[customer_phone] = {
                    "name": name,
                    "phone": customer_phone,
                    "debts": [],
                    "payments": [],
                    "balance": 0
                }

            customer = self.customers[customer_phone]
            customer["name"] = name

            debt = {
                "date": str(date.today()),
                "due_date": due,
                "items": [{
                    "product": product_key,
                    "quantity": qty,
                    "price": price,
                    "total": total,
                    "profit": profit
                }],
                "amount": total,
                "paid": 0,
                "balance": total
            }

            customer.setdefault("debts", []).append(debt)

            customer["balance"] = (
                float(customer.get("balance", 0))
                + total
            )

            pdata["stock"] -= qty

            self.sales.append({
                "receipt_number": self.next_receipt_number(),
                "date": str(date.today()),
                "items": debt["items"],
                "total": total,
                "profit": profit,
                "payment": "CREDIT",
                "customer": name,
                "phone": customer_phone,
                "due_date": due
            })

            self.save_all()

            self.popup(
                "Credit Sale Saved",
                f"Customer: {name}\n"
                f"Phone: {customer_phone}\n"
                f"Amount owed: {self.money(total)}\n"
                f"Due date: {due}"
            )

            customer_name.text = ""
            phone.text = ""
            product_name.text = ""
            quantity.text = ""
            due_date.text = ""

        save_button.bind(
            on_release=save_credit
        )

        content.add_widget(save_button)

        back_button = ShopButton(
            text="BACK",
            size_hint_y=None,
            height=dp(50)
        )

        back_button.bind(
            on_release=lambda x: self.show_home()
        )

        content.add_widget(back_button)

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # CUSTOMER PAYMENT
    # ---------------------------------------------------------

    def customer_payment(self, instance=None):
        self.page("CUSTOMER PAYMENT")

        scroll, content = self.scroll_area()

        phone = TextInput(
            hint_text="Customer phone",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(52)
        )

        amount = TextInput(
            hint_text="Payment amount",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(phone)
        content.add_widget(amount)

        pay = ShopButton(
            text="RECORD PAYMENT",
            size_hint_y=None,
            height=dp(58)
        )

        def record(_):
            customer_phone = phone.text.strip()

            if customer_phone not in self.customers:
                self.popup(
                    "Customer",
                    "Customer not found."
                )
                return

            customer = self.customers[customer_phone]

            balance = float(
                customer.get("balance", 0)
            )

            if balance <= 0:
                self.popup(
                    "Customer",
                    "This customer has no debt."
                )
                return

            try:
                payment_amount = float(amount.text)
            except ValueError:
                self.popup(
                    "Payment",
                    "Enter a valid amount."
                )
                return

            if payment_amount <= 0:
                self.popup(
                    "Payment",
                    "Payment must be greater than zero."
                )
                return

            if payment_amount > balance:
                self.popup(
                    "Payment",
                    f"Payment cannot exceed {self.money(balance)}."
                )
                return

            remaining = payment_amount

            for debt in customer.get("debts", []):
                if remaining <= 0:
                    break

                debt_balance = float(
                    debt.get("balance", 0)
                )

                if debt_balance <= 0:
                    continue

                payment = min(
                    remaining,
                    debt_balance
                )

                debt["paid"] = (
                    float(debt.get("paid", 0))
                    + payment
                )

                debt["balance"] = (
                    debt_balance - payment
                )

                remaining -= payment

            customer["balance"] = (
                balance - payment_amount
            )

            customer.setdefault(
                "payments", []
            ).append({
                "date": str(date.today()),
                "amount": payment_amount
            })

            self.save_all()

            self.popup(
                "Payment Recorded",
                f"Paid: {self.money(payment_amount)}\n"
                f"Remaining: {self.money(customer['balance'])}"
            )

            self.show_home()

        pay.bind(on_press=record)
        content.add_widget(pay)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # CUSTOMER HISTORY
    # ---------------------------------------------------------

    def customer_history(self, instance=None):
        self.page("CUSTOMER HISTORY")

        scroll, content = self.scroll_area()

        search = TextInput(
            hint_text="Customer name or phone",
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        content.add_widget(search)

        find_button = ShopButton(
            text="SEARCH CUSTOMER",
            size_hint_y=None,
            height=dp(55)
        )

        content.add_widget(find_button)

        results = Label(
            text="Enter a customer name or phone.",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(400)
        )

        content.add_widget(results)

        def find(_):
            query = search.text.strip().lower()

            if not query:
                results.text = "Enter a search value."
                return

            found = []

            for phone, customer in self.customers.items():
                if (
                    query in phone.lower()
                    or query in customer.get(
                        "name", ""
                    ).lower()
                ):
                    found.append(
                        (phone, customer)
                    )

            if not found:
                results.text = "Customer not found."
                return

            lines = []

            for phone, customer in found:
                lines.append(
                    f"CUSTOMER: {customer.get('name', '')}"
                )
                lines.append(
                    f"PHONE: {phone}"
                )
                lines.append(
                    f"BALANCE: {self.money(customer.get('balance', 0))}"
                )
                lines.append("")
                lines.append("DEBTS:")

                for debt in customer.get("debts", []):
                    lines.append(
                        f"Date: {debt.get('date', '')}"
                    )
                    lines.append(
                        f"Due: {debt.get('due_date', '')}"
                    )
                    lines.append(
                        f"Amount: {self.money(debt.get('amount', 0))}"
                    )
                    lines.append(
                        f"Paid: {self.money(debt.get('paid', 0))}"
                    )
                    lines.append(
                        f"Balance: {self.money(debt.get('balance', 0))}"
                    )

                    for item in debt.get("items", []):
                        lines.append(
                            f"  {item.get('product', '')} "
                            f"x {item.get('quantity', 0)}"
                        )

                lines.append("")
                lines.append("PAYMENTS:")

                for payment in customer.get(
                    "payments", []
                ):
                    lines.append(
                        f"{payment.get('date', '')} - "
                        f"{self.money(payment.get('amount', 0))}"
                    )

                lines.append(
                    "=============================="
                )

            results.text = "\n".join(lines)

        find_button.bind(on_press=find)

        content.add_widget(self.back_button())

        self.root.add_widget(scroll)

    # ---------------------------------------------------------
    # SETTINGS
    # ---------------------------------------------------------

    def show_settings(self, instance=None):
        self.page("SETTINGS")

        scroll, content = self.scroll_area()

        content.add_widget(
            self.label("MY SHOP SETTINGS")
        )

        content.add_widget(
            Label(
                text="Manage your shop application settings.",
                font_size=dp(16),
                size_hint_y=None,
                height=dp(45)
            )
        )

        content.add_widget(
            self.label("Shop Name")
        )

        shop_name = TextInput(
            text=self.settings.get(
                "shop_name",
                "MY SHOP"
            ),
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(shop_name)

        content.add_widget(
            self.label("Currency")
        )

        currency = TextInput(
            text=self.settings.get(
                "currency",
                "KSh"
            ),
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        content.add_widget(currency)

        save_button = ShopButton(
            text="SAVE SETTINGS",
            size_hint_y=None,
            height=dp(55)
        )

        def save_settings(instance):
            self.settings["shop_name"] = (
                shop_name.text.strip()
                or "MY SHOP"
            )

            self.settings["currency"] = (
                currency.text.strip()
                or "KSh"
            )

            self.save_all()

            self.popup(
                "Settings Saved",
                "Your shop settings have been saved successfully."
            )

        save_button.bind(
            on_release=save_settings
        )

        content.add_widget(save_button)

        back_button = ShopButton(
            text="BACK",
            size_hint_y=None,
            height=dp(50)
        )

        back_button.bind(
            on_release=lambda x: self.show_home()
        )

        content.add_widget(back_button)

        self.root.add_widget(scroll)


if __name__ == "__main__":
    MyShopApp().run()
