from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class PhoneVerificationError(Exception):
    pass


class Phone(Field):
    def __init__(self, value: str):
        self.verify_phone(value=value)
        super().__init__(value)

    @staticmethod
    def verify_phone(value: str):
        if not isinstance(value, str):
            raise PhoneVerificationError(f"Incorrect phone data type given: {type(value)}, must be 'str'")
        if len(value) != 10:
            raise PhoneVerificationError("Incorrect length of phone, must be 10 digits")
        if not value.isdigit():
            raise PhoneVerificationError(f"Phone must include only numbers, '{value}' is not a number")


class Birthday(Field):
    def __init__(self, value):
        self.verify_birthday(value=value)
        super().__init__(value)

    @staticmethod
    def verify_birthday(value: str):
        if not isinstance(value, str):
            raise ValueError("Value provided is not of 'str' format")
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str) -> None | str:
        for phone_record in self.phones:
            if phone_record.value == phone:
                return "Phone already in the record!"

        self.phones.append(Phone(phone))

    def add_birthday(self, value: str) -> None | str:
        if self.birthday:
            return "Birthday is already in the record!"
        self.birthday = Birthday(value)

    def remove_phone(self, phone: str) -> None | str:
        for phone_record in self.phones:
            if phone_record.value == phone:
                self.phones.remove(phone_record)
        else:
            return "Phone you are trying to remove is not in the record. Add the phone"

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        try:
            for phone_record in self.phones:
                if phone_record.value == old_phone:
                    Phone.verify_phone(new_phone)
                    phone_record.value = new_phone
                    return
            else:
                raise ValueError(
                    "Incorrect input. Phone you are trying to edit "
                    "is not in the record or incorrect input type given, "
                    "must be 'str'."
                )
        except PhoneVerificationError as e:
            raise ValueError(e)

    def find_phone(self, phone: str):
        return next(
            (phone_record for phone_record in self.phones if phone_record.value == phone),
            None
        )

    def __str__(self) -> str:
        return (
            f"Contact name: {self.name.value} , "
            f"phones: {'; '.join((p.value if self.phones else None) for p in self.phones)}"
        )


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name in self.data.keys():
            del self.data[name]

    def __str__(self) -> str:
        return '\n'.join(str(self.data[record]) for record in self.data)

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today()

        def string_to_date(date_string):
            return datetime.strptime(date_string, "%d.%m.%Y")

        def date_to_string(birth_date):
            return birth_date.strftime("%d.%m.%Y")

        def find_next_weekday(start_date, weekday):
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        def adjust_for_weekend(birthday):
            if birthday.weekday() >= 5:
                return find_next_weekday(birthday, 0)
            return birthday

        for user in self.data:
            if self.data[user].birthday:
                birthday_date = string_to_date(self.data[user].birthday.value)
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:
                    birthday_this_year = adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = date_to_string(birthday_this_year)
                    upcoming_birthdays.append(
                        {
                            "name": self.data[user].name.value.__str__(),
                            "birthday": congratulation_date_str
                        }
                    )
        return upcoming_birthdays
