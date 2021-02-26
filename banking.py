import random
import sqlite3

connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
connection.commit()
cursor.execute("DROP TABLE IF EXISTS card;")
cursor.execute(
    """CREATE TABLE card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
);"""
)
connection.commit()


class Account:
    INN = [4, 0, 0, 0, 0, 0]

    def generate_new_data(self):

        # find the next id for a card
        cursor.execute("""
            SELECT * FROM card;
        """)
        next_id = len(cursor.fetchall()) + 1

        # insert a new row into database
        card_number = self.generate_card_number()
        pin = self.generate_pin()
        # print(f"Value of generated pin: {pin}, type of pin: {type(pin)}")
        cursor.execute('INSERT INTO card (id, number, pin) VALUES( {}, "{}", "{}");'.format(next_id, card_number, pin))
        connection.commit()

        cursor.execute("""
            SELECT number, pin FROM card WHERE id = {};
        """.format(next_id))
        new_card_data = cursor.fetchone()
        # print(f"Value of fetched pin: {new_card_data[1]}, type of pin: {type(new_card_data[1])}")
        print("Your card has been created")
        print("Your card number:")
        print(new_card_data[0])
        print("Your card PIN:")
        print(new_card_data[1])

        self.print_start_menu()

    def generate_card_number(self):
        customer_account_number = []
        i = 0
        while i < 9:
            customer_account_number.append(random.randint(0, 9))
            i += 1

        checksum = self.generate_checksum(customer_account_number)
        account_number = self.INN + customer_account_number + checksum
        card_number = ''.join(str(x) for x in account_number)

        return card_number

    @staticmethod
    def generate_pin():
        pin = []
        i = 0
        while i < 4:
            pin.append(random.randint(0, 9))
            i += 1
        pin = ''.join(str(x) for x in pin)
        # print(f"Pin of type {type(pin)} has value of {pin}")
        return ''.join(str(x) for x in pin)

    def generate_checksum(self, customer_account_number):
        partial_card_number = self.INN + customer_account_number
        # print(int(''.join(str(x) for x in partial_card_number)))
        # partial_card_number = [4, 0, 0, 0, 0, 0, 8, 4, 4, 9, 4, 3, 3, 4, 0]
        partial_sum = 0
        index = 1
        # checksum = []
        # TODO: Make a separate method for Luhn algorithm!
        for digit in partial_card_number:
            if index % 2 == 0:
                partial_sum += digit
            elif index % 2 == 1:
                temp = digit * 2
                if temp > 9:
                    partial_sum += temp - 9
                elif temp < 10:
                    partial_sum += temp
            index += 1

        if partial_sum % 10 > 0:
            checksum = [10 - partial_sum % 10]
        else:
            checksum = [0]

        return checksum

    def auth_card_number(self):
        input_card_number = input("Enter your card number:")
        input_pin = input("Enter your PIN:")

        cursor.execute("""
            SELECT 
                id, 
                number, 
                pin 
                FROM 
                    card 
                WHERE 
                    number = '{}' 
                AND pin = '{}';
        """.format(input_card_number, input_pin))
        if len(cursor.fetchall()) > 0:
            print("You have successfully logged in!")
            self.print_account_menu(input_card_number)
        else:
            print("Wrong card number or PIN!")
            self.print_start_menu()

    def print_account_menu(self, card_number):
        print("1. Balance\n"
              "2. Add income\n"
              "3. Do transfer\n"
              "4. Close account\n"
              "5. Log out\n"
              "0. Exit")
        login_choice = int(input())
        if login_choice == 0:  # Exit
            print("Bye!")

        elif login_choice == 1:  # Check balance
            print(f"Balance: {self.check_balance(card_number)}")
            self.print_account_menu(card_number)

        elif login_choice == 2:  # Add income
            self.add_income(card_number)
            self.print_account_menu(card_number)

        elif login_choice == 3:
            self.do_transfer(card_number)
            self.print_account_menu(card_number)

        elif login_choice == 4:
            self.close_account(card_number)
            self.print_start_menu()

        elif login_choice == 5:  # Log out
            self.print_start_menu()

    def print_start_menu(self):

        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = int(input())
        if choice == 0:  # exit program
            print("Bye!")
        elif choice == 1:  # new account
            self.generate_new_data()
        elif choice == 2:  # auth
            self.auth_card_number()

    @staticmethod
    def check_balance(card_number):
        cursor.execute(f"""
            SELECT 
                balance 
                FROM 
                    card 
                WHERE 
                    number = {card_number};
            """)
        return cursor.fetchone()[0]

    def add_income(self, card_number):
        current_balance = self.check_balance(card_number)
        addition = int(input("Enter income:"))
        cursor.execute(
            "UPDATE card SET balance = {} WHERE number = '{}';".format(current_balance + addition, card_number))
        connection.commit()
        print("Income was added!")

    def do_transfer(self, card_number):
        print("Transfer")
        print("Enter card number:")
        searched_card_number = input()
        if self.validate_card_number(searched_card_number):
            print("Enter how much money you want to transfer:")
            transfer_amount = int(input())
            if self.check_balance(card_number) < transfer_amount:
                print("Not enough money!")
            else:
                user_new_balance = self.check_balance(card_number) - transfer_amount
                cursor.execute("""
                    UPDATE card SET balance = {} WHERE number = '{}';
                """.format(user_new_balance, card_number))
                connection.commit()
                second_user_new_balance = self.check_balance(searched_card_number) + transfer_amount
                cursor.execute("""
                    UPDATE card SET balance = {} WHERE number = '{}';
                """.format(second_user_new_balance, searched_card_number))
                connection.commit()
                print("Success!")

    @staticmethod
    def validate_card_number(searched_card_number):
        print("===========================")
        print(f"Searched card number: {searched_card_number}")
        partial_card_number = list(searched_card_number)

        last_card_digit = int(partial_card_number.pop())
        print(f"Partial card number: {partial_card_number}")
        index = 1
        partial_sum = 0
        for digit in partial_card_number:
            if index % 2 == 0:
                partial_sum += int(digit)
            elif index % 2 == 1:
                temp = int(digit) * 2
                if temp > 9:
                    partial_sum += temp - 9
                elif temp < 10:
                    partial_sum += temp
            index += 1

        print(f"Partial sum: {partial_sum}")
        if partial_sum % 10 > 0:
            checksum = [10 - partial_sum % 10]
        else:
            checksum = [0]
        print(f"Supposed checksum: {checksum[0]} {type(checksum[0])}")
        print(f"Last card digit: {last_card_digit} {type(last_card_digit)}")
        print("===========================")
        if checksum[0] == last_card_digit:
            cursor.execute("""
                SELECT * from card WHERE number = '{}'
            """.format(searched_card_number))
            if len(cursor.fetchall()) < 1:
                print("Such a card does not exist.")
                return False
            else:
                return True
        else:
            print("Probably you made a mistake in the card number. Please try again!")
            return False

    def close_account(self, card_number):
        cursor.execute("""
            DELETE FROM card WHERE number = {}
        """.format(card_number))
        connection.commit()
        print("The account has been closed!")


Account().print_start_menu()
