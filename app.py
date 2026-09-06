import json
from datetime import date, datetime, timedelta

PRODUCT_FILE = "products.json"
SALES_FILE = "sales.json"
CUSTOMER_FILE = "customers.json"
EXPENSE_FILE = "expenses.json"
SETTINGS_FILE = "settings.json"


def load_data(filename, default):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


products = load_data(PRODUCT_FILE, {})
sales = load_data(SALES_FILE, [])
customers = load_data(CUSTOMER_FILE, {})
expenses = load_data(EXPENSE_FILE, [])
settings = load_data(SETTINGS_FILE, {
    "shop_name": "MY SHOP",
    "currency": "KSh"
})


def save_all():
    files = [
        (PRODUCT_FILE, products),
        (SALES_FILE, sales),
        (CUSTOMER_FILE, customers),
        (EXPENSE_FILE, expenses),
        (SETTINGS_FILE, settings),
    ]
    for filename, data in files:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


def money(value):
    return f'{settings.get("currency", "KSh")} {float(value):,.2f}'


def new_product_code():
    number = 1
    used_codes = {str(p.get("code", "")) for p in products.values()}
    while str(number).zfill(3) in used_codes:
        number += 1
    return str(number).zfill(3)


def find_product(code):
    code = str(code).strip()
    for name, product in products.items():
        if str(product.get("code", "")) == code:
            return name
    return None


def add_product():
    print("\n===== ADD PRODUCT =====")
    name = input("Product name: ").strip()
    if not name:
        print("Product name cannot be empty.")
        return
    if name in products:
        print("Product already exists.")
        return

    categories = {
        "1": "Food", "2": "Drinks", "3": "Household",
        "4": "Clothes", "5": "Electronics", "6": "Other"
    }
    print("\nCategories:")
    for key, value in categories.items():
        print(f"{key}. {value}")
    category_choice = input("Choose category: ").strip()
    if category_choice not in categories:
        print("Invalid category.")
        return

    try:
        buying = float(input("Buying price KSh: "))
        selling = float(input("Selling price KSh: "))
        stock = int(input("Starting stock: "))
        if buying < 0 or selling < 0 or stock < 0:
            raise ValueError
    except ValueError:
        print("Please enter valid non-negative numbers.")
        return

    code = new_product_code()
    products[name] = {
        "code": code,
        "category": categories[category_choice],
        "buying": buying,
        "selling": selling,
        "stock": stock
    }
    save_all()
    print("\nProduct added successfully!")
    print("Product code:", code)


def view_products():
    print("\n===== PRODUCTS =====")
    if not products:
        print("No products available.")
        return
    for name, product in products.items():
        stock = product.get("stock", 0)
        warning = " ⚠️ LOW STOCK" if stock <= 5 else ""
        print(
            f'{product.get("code", "N/A")} | {name} | '
            f'{product.get("category", "Other")} | '
            f'Buy {money(product.get("buying", 0))} | '
            f'Sell {money(product.get("selling", 0))} | '
            f'Stock {stock}{warning}'
        )


def make_cart():
    cart = []
    print("\n===== ADD PRODUCTS TO SALE =====")
    print("Type product name or code. Type DONE when finished.")
    while True:
        search = input("\nProduct name/code: ").strip()
        if search.upper() == "DONE":
            break
        if not search:
            continue

        search_lower = search.lower()
        matches = [
            (name, product)
            for name, product in products.items()
            if search_lower in name.lower()
            or search_lower in str(product.get("code", "")).lower()
        ]

        if not matches:
            print("Product not found.")
            continue

        if len(matches) > 1:
            print("\nProducts found:")
            for number, (name, product) in enumerate(matches, 1):
                print(
                    f'{number}. {name} | Stock: {product.get("stock", 0)} | '
                    f'Price: {money(product.get("selling", 0))}'
                )
            try:
                selected = int(input("Choose product number: "))
                if not 1 <= selected <= len(matches):
                    print("Invalid choice.")
                    continue
                name, product = matches[selected - 1]
            except ValueError:
                print("Enter a number.")
                continue
        else:
            name, product = matches[0]

        print("Selected:", name)
        print("Selling price:", money(product.get("selling", 0)))
        print("Available stock:", product.get("stock", 0))

        try:
            quantity = int(input("Quantity: "))
        except ValueError:
            print("Enter a valid quantity.")
            continue

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            continue

        already = sum(
            item["quantity"] for item in cart
            if item["product"] == name
        )
        available = product.get("stock", 0) - already

        if quantity > available:
            print("Not enough stock. Available:", available)
            continue

        price = float(product.get("selling", 0))
        buying = float(product.get("buying", 0))
        cart.append({
            "product": name,
            "quantity": quantity,
            "price": price,
            "total": quantity * price,
            "profit": quantity * (price - buying)
        })
        print("Added:", name, "x", quantity)
        print("Item total:", money(quantity * price))

    return cart


def show_cart(cart):
    print("\n================================")
    print("          CART PREVIEW")
    print("================================")
    if not cart:
        print("Cart is empty.")
        return 0

    total = 0
    for number, item in enumerate(cart, 1):
        print(
            f'{number}. {item["product"]} | Qty: {item["quantity"]} | '
            f'Price: {money(item["price"])} | Total: {money(item["total"])}'
        )
        total += item["total"]

    print("--------------------------------")
    print("TOTAL:", money(total))
    print("================================")
    return total


def edit_cart(cart):
    while cart:
        print("\n===== EDIT CART =====")
        for number, item in enumerate(cart, 1):
            print(
                f'{number}. {item["product"]} x {item["quantity"]} = '
                f'{money(item["total"])}'
            )
        print("1. Change quantity")
        print("2. Remove item")
        print("3. Finish editing")

        choice = input("Choose: ").strip()
        if choice == "3":
            return

        try:
            number = int(input("Item number: "))
            if not 1 <= number <= len(cart):
                print("Invalid item number.")
                continue
        except ValueError:
            print("Enter a valid number.")
            continue

        item = cart[number - 1]

        if choice == "1":
            try:
                quantity = int(input("New quantity: "))
            except ValueError:
                print("Enter a valid number.")
                continue

            if quantity <= 0:
                print("Quantity must be greater than zero.")
                continue

            product = products[item["product"]]
            other_quantity = sum(
                x["quantity"]
                for i, x in enumerate(cart)
                if i != number - 1 and x["product"] == item["product"]
            )

            if quantity > product.get("stock", 0) - other_quantity:
                print("Not enough stock.")
                continue

            item["quantity"] = quantity
            item["total"] = quantity * item["price"]
            item["profit"] = quantity * (
                item["price"] - product.get("buying", 0)
            )
            print("Quantity updated.")

        elif choice == "2":
            removed = cart.pop(number - 1)
            print("Removed:", removed["product"])
        else:
            print("Invalid choice.")

    print("Cart is empty.")


def next_receipt_number():
    numbers = []
    for sale in sales:
        try:
            numbers.append(int(sale.get("receipt_number", 0)))
        except (ValueError, TypeError):
            pass
    return str((max(numbers) if numbers else 0) + 1).zfill(6)


def print_receipt(
    cart, total, payment, customer_name="", phone="",
    cash=0, change=0, reference="", receipt_number=""
):
    print("\n================================")
    print(f'            {settings.get("shop_name", "MY SHOP")}')
    print("         SALES RECEIPT")
    print("================================")
    print("Receipt No:", receipt_number)
    print("Date:", date.today())

    if customer_name:
        print("Customer:", customer_name)
    if phone:
        print("Phone:", phone)

    print("--------------------------------")
    for item in cart:
        print(f'{item["product"]} x {item["quantity"]}')
        print(
            f'  {money(item["price"])} each = '
            f'{money(item["total"])}'
        )

    print("--------------------------------")
    print("TOTAL:", money(total))
    print("PAYMENT:", payment)

    if payment == "CASH":
        print("Received:", money(cash))
        print("Change:", money(change))
    elif payment == "M-PESA":
        print("M-Pesa Ref:", reference)
    elif payment == "CREDIT":
        print("STATUS: PAY LATER")
        print("AMOUNT OWED:", money(total))

    print("================================")
    print("       THANK YOU FOR SHOPPING")
    print("================================")


def complete_sale(
    cart, payment, customer_name="", phone="",
    cash=0, reference="", due_date=""
):
    total = sum(item["total"] for item in cart)
    profit = sum(item["profit"] for item in cart)

    if payment == "CASH":
        change = cash - total
    else:
        change = 0

    receipt_number = next_receipt_number()

    for item in cart:
        products[item["product"]]["stock"] -= item["quantity"]

    sale = {
        "receipt_number": receipt_number,
        "date": str(date.today()),
        "items": cart,
        "total": total,
        "profit": profit,
        "payment": payment,
        "customer": customer_name,
        "phone": phone,
        "reference": reference
    }

    if payment == "CASH":
        sale["cash_received"] = cash
        sale["change"] = change

    if payment == "CREDIT":
        sale["due_date"] = due_date

    sales.append(sale)
    save_all()

    print_receipt(
        cart, total, payment, customer_name, phone,
        cash, change, reference, receipt_number
    )


def normal_sale():
    print("\n===== NEW SALE =====")
    cart = make_cart()

    if not cart:
        print("No sale made.")
        return

    while True:
        total = show_cart(cart)

        if not cart:
            print("Sale cancelled.")
            return

        print("1. Continue to payment")
        print("2. Edit cart")
        print("3. Cancel sale")

        choice = input("Choose: ").strip()

        if choice == "1":
            break
        if choice == "2":
            edit_cart(cart)
        elif choice == "3":
            print("Sale cancelled.")
            return
        else:
            print("Invalid choice.")

    print("\n===== PAYMENT METHOD =====")
    print("1. CASH")
    print("2. M-PESA")

    choice = input("Choose: ").strip()

    if choice == "1":
        try:
            cash = float(input("Cash received: "))
        except ValueError:
            print("Invalid amount.")
            return

        if cash < total:
            print("Not enough cash. Required:", money(total))
            return

        complete_sale(cart, "CASH", cash=cash)

    elif choice == "2":
        reference = input("M-Pesa transaction code: ").strip().upper()

        if not reference:
            print("Enter the M-Pesa reference.")
            return

        complete_sale(cart, "M-PESA", reference=reference)
    else:
        print("Invalid payment method.")


def credit_sale():
    print("\n===== PAY LATER =====")
    name = input("Customer name: ").strip()
    phone = input("Customer phone: ").strip()

    if not name or not phone:
        print("Name and phone are required.")
        return

    cart = make_cart()

    if not cart:
        print("No credit sale made.")
        return

    total = show_cart(cart)

    print("\n1. Confirm PAY LATER")
    print("2. Cancel")

    if input("Choose: ").strip() != "1":
        print("Credit sale cancelled.")
        return

    due_date = input("Payment due date (YYYY-MM-DD): ").strip()

    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            print("Invalid due date. Use YYYY-MM-DD.")
            return

    customer = customers.setdefault(
        phone,
        {
            "name": name,
            "phone": phone,
            "debts": [],
            "payments": [],
            "balance": 0
        }
    )

    customer["name"] = name

    debt = {
        "date": str(date.today()),
        "due_date": due_date,
        "items": cart,
        "amount": total,
        "paid": 0,
        "balance": total
    }

    customer.setdefault("debts", []).append(debt)
    customer["balance"] = customer.get("balance", 0) + total

    for item in cart:
        products[item["product"]]["stock"] -= item["quantity"]

    sales.append({
        "receipt_number": next_receipt_number(),
        "date": str(date.today()),
        "items": cart,
        "total": total,
        "profit": sum(i["profit"] for i in cart),
        "payment": "CREDIT",
        "customer": name,
        "phone": phone,
        "due_date": due_date
    })

    save_all()

    print("\nCREDIT SAVED")
    print("Customer:", name)
    print("Phone:", phone)
    print("Amount owed:", money(total))
    print("Due date:", due_date or "Not specified")
    print("Total customer balance:", money(customer["balance"]))


def view_customers():
    print("\n===== CUSTOMERS WHO OWE =====")
    found = False
    total_debt = 0
    today = date.today()

    for phone, customer in customers.items():
        balance = float(customer.get("balance", 0))

        if balance > 0:
            found = True
            total_debt += balance

            print("--------------------------------")
            print("Name:", customer.get("name", ""))
            print("Phone:", phone)
            print("TOTAL OWES:", money(balance))

            for debt in customer.get("debts", []):
                debt_balance = float(debt.get("balance", 0))

                if debt_balance <= 0:
                    continue

                due = debt.get("due_date", "")
                overdue = False

                try:
                    overdue = (
                        bool(due)
                        and date.fromisoformat(due) < today
                    )
                except ValueError:
                    pass

                print(
                    ("OVERDUE | " if overdue else "Due: ")
                    + (due or "Not specified")
                    + " | Balance: "
                    + money(debt_balance)
                )

    print("--------------------------------")

    if found:
        print("TOTAL MONEY OWED:", money(total_debt))
    else:
        print("Nobody currently owes money.")


def customer_history():
    print("\n===== CUSTOMER SEARCH =====")
    search = input("Enter customer name or phone: ").strip().lower()
    found = False

    for phone, customer in customers.items():
        if (
            search in customer.get("name", "").lower()
            or search in phone
        ):
            found = True

            print("\n================================")
            print("CUSTOMER:", customer.get("name", ""))
            print("PHONE:", phone)
            print("TOTAL BALANCE:", money(customer.get("balance", 0)))
            print("================================")

            print("\nDEBTS:")
            for debt in customer.get("debts", []):
                print(
                    f'Date: {debt.get("date", "")} | '
                    f'Due: {debt.get("due_date", "")} | '
                    f'Amount: {money(debt.get("amount", 0))} | '
                    f'Paid: {money(debt.get("paid", 0))} | '
                    f'Balance: {money(debt.get("balance", 0))}'
                )

                for item in debt.get("items", []):
                    print(
                        f'  {item["product"]} x '
                        f'{item["quantity"]}'
                    )

            print("\nPAYMENTS:")
            for payment in customer.get("payments", []):
                print(
                    payment.get("date", ""),
                    "|",
                    money(payment.get("amount", 0))
                )

    if not found:
        print("Customer not found.")


def customer_payment():
    print("\n===== CUSTOMER PAYMENT =====")
    phone = input("Customer phone: ").strip()

    if phone not in customers:
        print("Customer not found.")
        return

    customer = customers[phone]
    balance = float(customer.get("balance", 0))

    print("Customer:", customer.get("name", ""))
    print("Current balance:", money(balance))

    if balance <= 0:
        print("This customer has no debt.")
        return

    try:
        amount = float(input("Payment received: "))
    except ValueError:
        print("Invalid amount.")
        return

    if amount <= 0 or amount > balance:
        print(
            "Payment must be greater than zero and "
            "not exceed the debt."
        )
        return

    remaining = amount

    for debt in customer.get("debts", []):
        if remaining <= 0:
            break

        debt_balance = float(debt.get("balance", 0))

        if debt_balance <= 0:
            continue

        payment = min(remaining, debt_balance)
        debt["paid"] = float(debt.get("paid", 0)) + payment
        debt["balance"] = debt_balance - payment
        remaining -= payment

    customer["balance"] = balance - amount

    customer.setdefault("payments", []).append({
        "date": str(date.today()),
        "amount": amount
    })

    save_all()

    print("Payment recorded.")
    print("Amount paid:", money(amount))
    print("Remaining balance:", money(customer["balance"]))
    print(
        "STATUS:",
        "PAID" if customer["balance"] == 0 else "OWING"
    )


def add_expense():
    print("\n===== ADD EXPENSE =====")
    description = input("Expense description: ").strip()

    if not description:
        print("Description cannot be empty.")
        return

    try:
        amount = float(input("Amount KSh: "))

        if amount <= 0:
            raise ValueError
    except ValueError:
        print("Enter a valid positive amount.")
        return

    expenses.append({
        "date": str(date.today()),
        "description": description,
        "amount": amount
    })

    save_all()
    print("Expense saved.")


def add_stock():
    view_products()
    code = input("\nProduct code: ").strip()
    name = find_product(code)

    if not name:
        print("Product not found.")
        return

    try:
        quantity = int(input("Quantity to add: "))

        if quantity <= 0:
            raise ValueError
    except ValueError:
        print("Enter a valid positive whole number.")
        return

    products[name]["stock"] += quantity
    save_all()

    print(
        "Stock updated. New stock:",
        products[name]["stock"]
    )


def today_report():
    report_for_period(
        date.today(),
        date.today(),
        "TODAY'S REPORT"
    )


def report_for_period(start_date, end_date, title):
    start_text = str(start_date)
    end_text = str(end_date)

    period_sales = [
        s for s in sales
        if start_text <= s.get("date", "") <= end_text
    ]

    period_expenses = [
        e for e in expenses
        if start_text <= e.get("date", "") <= end_text
    ]

    total_sales = sum(
        float(s.get("total", 0)) for s in period_sales
    )
    total_profit = sum(
        float(s.get("profit", 0)) for s in period_sales
    )
    total_expenses = sum(
        float(e.get("amount", 0)) for e in period_expenses
    )

    print("\n================================")
    print(settings.get("shop_name", "MY SHOP"))
    print(title)
    print("================================")
    print("From:", start_text)
    print("To:", end_text)
    print("--------------------------------")
    print("Sales:", money(total_sales))
    print("Gross profit:", money(total_profit))
    print("Expenses:", money(total_expenses))
    print("NET PROFIT:", money(total_profit - total_expenses))
    print("--------------------------------")
    print("Number of sales:", len(period_sales))
    print("Number of expenses:", len(period_expenses))
    print("================================")


def dashboard():
    total_stock = sum(
        int(p.get("stock", 0)) for p in products.values()
    )
    low_stock_count = sum(
        1 for p in products.values()
        if p.get("stock", 0) <= 5
    )

    customers_owing = 0
    total_debt = 0
    overdue_debt = 0
    today = date.today()

    for customer in customers.values():
        balance = float(customer.get("balance", 0))

        if balance > 0:
            customers_owing += 1
            total_debt += balance

            for debt in customer.get("debts", []):
                db = float(debt.get("balance", 0))

                try:
                    if (
                        db > 0
                        and debt.get("due_date")
                        and date.fromisoformat(
                            debt["due_date"]
                        ) < today
                    ):
                        overdue_debt += db
                except ValueError:
                    pass

    today_text = str(today)

    today_sales = sum(
        float(s.get("total", 0))
        for s in sales
        if s.get("date") == today_text
    )

    today_profit = sum(
        float(s.get("profit", 0))
        for s in sales
        if s.get("date") == today_text
    )

    today_expenses = sum(
        float(e.get("amount", 0))
        for e in expenses
        if e.get("date") == today_text
    )

    print("\n================================")
    print(settings.get("shop_name", "MY SHOP"))
    print("         DASHBOARD")
    print("================================")
    print("Products:", len(products))
    print("Total stock:", total_stock)
    print("Low-stock products:", low_stock_count)
    print("--------------------------------")
    print("Today's sales:", money(today_sales))
    print("Today's profit:", money(today_profit))
    print("Today's expenses:", money(today_expenses))
    print(
        "Today's net profit:",
        money(today_profit - today_expenses)
    )
    print("--------------------------------")
    print("Customers owing:", customers_owing)
    print("Total money owed:", money(total_debt))
    print("Overdue debt:", money(overdue_debt))
    print("================================")


def settings_menu():
    global settings

    print("\n===== SETTINGS =====")
    print("1. Change shop name")
    print("2. Change currency")
    print("3. View current settings")
    print("4. Reset settings")
    print("5. Back")

    choice = input("Choose: ").strip()

    if choice == "1":
        name = input("Enter shop name: ").strip()
        if name:
            settings["shop_name"] = name
            save_all()
            print("Shop name saved.")
        else:
            print("Shop name cannot be empty.")

    elif choice == "2":
        currency = input("Enter currency symbol/name: ").strip()
        if currency:
            settings["currency"] = currency
            save_all()
            print("Currency saved.")
        else:
            print("Currency cannot be empty.")

    elif choice == "3":
        print("\nCurrent settings:")
        print("Shop name:", settings.get("shop_name", "MY SHOP"))
        print("Currency:", settings.get("currency", "KSh"))

    elif choice == "4":
        settings["shop_name"] = "MY SHOP"
        settings["currency"] = "KSh"
        save_all()
        print("Settings reset.")

    elif choice == "5":
        return

    else:
        print("Invalid choice.")


def main_menu():
    while True:
        print("\n================================")
        print(f'          {settings.get("shop_name", "MY SHOP")}')
        print("================================")
        print("1. Dashboard")
        print("2. Add product")
        print("3. View products")
        print("4. New sale")
        print("5. Pay later")
        print("6. Customers")
        print("7. Customer payment")
        print("8. Customer history")
        print("9. Today's report")
        print("10. Add expense")
        print("11. Add stock")
        print("12. Settings")
        print("13. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            dashboard()
        elif choice == "2":
            add_product()
        elif choice == "3":
            view_products()
        elif choice == "4":
            normal_sale()
        elif choice == "5":
            credit_sale()
        elif choice == "6":
            view_customers()
        elif choice == "7":
            customer_payment()
        elif choice == "8":
            customer_history()
        elif choice == "9":
            today_report()
        elif choice == "10":
            add_expense()
        elif choice == "11":
            add_stock()
        elif choice == "12":
            settings_menu()
        elif choice == "13":
            save_all()
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
