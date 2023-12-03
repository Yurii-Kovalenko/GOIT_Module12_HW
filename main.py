from collections import UserDict

from re import sub

from datetime import datetime

from random import randint

from pathlib import Path

from json import load

from json import dump

from json import loads

from json import dumps


IS_DATE_GERMAN = True

IS_DATE_AMERICAN = not IS_DATE_GERMAN

if IS_DATE_GERMAN:
    DATE_TEMPLATE = "%d.%m.%Y"
    DATE_PROMPT = "DD.MM.YYYY"
else:
    DATE_TEMPLATE = "%m/%d/%Y"
    DATE_PROMPT = "MM/DD/YYYY"

WAIT_FOR_ENTER = "Press 'Enter' to continue."

NAME_FILE = "contacts.json"

class Field:
    def __init__(self, value: str):
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        self.__value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        self.__value = None
        self.value = value


class Phone(Field):
    def __init__(self, value: str):
        self.__value = None
        self.value = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        value = sub(r'\D', '', value)
        if len(value) == 10:
            self.__value = value
        else:
            self.__value = ""
            print(f"Incorrect phone number {value}.")


class Birthday(Field):
    def __init__(self, value: str):
        self.__value = None
        self.value = value
    
    @property
    def value(self) -> datetime:
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        if value != "" and type(value) == str:
            try:
                self.__value = datetime.strptime(value, DATE_TEMPLATE)
            except:
                print(f"Incorrect date {value}. Date in format {DATE_PROMPT} is required.")
                self.__value = ""
        else:
            self.__value = ""
    
    def __str__(self) -> str:
        if type(self.value) == str:
            return ""
        else:
            return self.value.strftime(DATE_TEMPLATE)
           

class Record:
    def __init__(self, name: str, birthday = Birthday("")):
        self.name = Name(name)
        if birthday:
            self.birthday = Birthday(birthday)
        self.phones = []

    def add_phone(self, phone: str) -> None:
        new_phone = Phone(phone)
        if new_phone.value:
            self.phones.append(new_phone)

    def remove_phone(self, phone: str) -> None:
        not_found = True
        for exemplar_phone in self.phones:
            if exemplar_phone.value == phone:
                    self.phones.remove(exemplar_phone)
                    not_found = False
                    break
        if not_found:
            print(f"Phone number {phone} not found.")
    
    def edit_phone(self, phone_old: str, phone_new: str) -> None:
        not_found = True
        for exemplar_phone in self.phones:
            if exemplar_phone.value == phone_old:
                exemplar_phone.value = phone_new
                if not exemplar_phone.value:
                    exemplar_phone.value = phone_old
                not_found = False
                break
        if not_found:
            print(f"Phone number {phone_old} not found.")
    
    def find_phone(self, phone: str) -> Phone:
        not_found = True
        for exemplar_phone in self.phones:
            if exemplar_phone.value == phone:
                not_found = False
                break
        if not_found:
            print(f"Phone number {phone} not found.")
        return None if not_found else exemplar_phone
    
    def days_to_birthday(self) -> int:
        if type(self.birthday.value) == str:
            return None
        else:
            date_of_birth : datetime = self.birthday.value
            today_date = datetime.today()
            today_date = datetime(today_date.year,
                                  today_date.month,
                                  today_date.day)
            new_date_birthday = datetime(today_date.year,
                                         date_of_birth.month,
                                         date_of_birth.day)
            time_delta = new_date_birthday - today_date
            if time_delta.days < 0:
                new_date_birthday = datetime(today_date.year + 1,
                                             date_of_birth.month,
                                             date_of_birth.day)
                time_delta = new_date_birthday - today_date
            return time_delta.days
    

    def __str__(self) -> str:
        if type(self.birthday.value) == str:
            birthday_text = ""
        else:
            birthday_text = f", birthday: {self.birthday.value.strftime(DATE_TEMPLATE)}"
        if len(self.phones) > 0:
            s = ""
            if len(self.phones) > 1:
                s = "s"
            phones_text = f", phone{s}: {'; '.join(phone.value for phone in self.phones)}"
        else:
            phones_text = ""
        return f"Contact name: {self.name.value}{birthday_text}{phones_text}"
               

class AddressBook(UserDict):
    def __init__(self):
        self.data = dict()
        self.filename = Path(Path.home() / NAME_FILE)
    
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name_search: str) -> Record:
        for key in self.data:
            if key == name_search:
                return self.data[key]

    def delete(self, name_search: str) -> None:
        for key in self.data:
            if key == name_search:
                break
        self.data.pop(key)

    def iterator(self, item_number: int) -> str:
        counter = 0
        result = []
        for record in self.data.values():
            result.append(str(record))
            counter += 1
            if counter >= item_number:
                yield "\n".join(result)
                counter = 0
                result = []
        if result:
            yield "\n".join(result)
    
    def find_by_string(self, string: str) -> str:
        result = []
        for record in self.data.values():
            is_match = string in record.name.value
            for phone in record.phones:
                if is_match:
                    break
                is_match = is_match or (string in phone.value)
            if is_match:
                result.append(str(record))
        return "\n".join(result)

    def load_from_file(self):
        if not self.filename.exists():
            return
        with open(self.filename, "r") as fr:
            data_json = load(fr)
            records = data_json["contacts"]
            for record_json in records:
                new_record = Record(record_json["name"], record_json["birthday"])
                for phone in record_json["phones"]:
                    new_record.add_phone(phone)
                self.add_record(new_record)

    def save_to_file(self):
        records = []
        for record in self.data.values():
                record_json = {"name": record.name.value,
                              "birthday": str(record.birthday),
                              "phones": [phone.value for phone in record.phones] }
                records.append(record_json)
        with open(self.filename, "w") as fw:
            dump({"contacts": records}, fw)


if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()
    book.load_from_file()

    first_record = Record("First")
    print(first_record)

    # Створення запису для John
    john_record = Record("John", "26.11.2002")
    print(john_record)

    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_phone("7777777777")
    john_record.remove_phone("7777777777")

    print(john_record.name, john_record.birthday, john_record.days_to_birthday())

    # Додавання запису John до адресної книги
    # book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    # jane_record = Record("Jane")
    # jane_record.add_phone("9876543210")
    # book.add_record(jane_record)


    # Виведення всіх записів у книзі по 5 записів
    # for text in book.iterator(5):
    #     print(text)
    #     input(WAIT_FOR_ENTER)

    # # Знаходження та редагування телефону для John
    # john = book.find("John")
    # john.edit_phone("1234567890", "1112223333")

    # print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    # found_phone = john.find_phone("5555555555")
    # print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    # book.delete("Jane")

    
    # Додавання до книги двадцяти випадкових записів
    # connt_record = 20
    # rand_name = ["Emman", "Jeffrey", "Dorian", "Carson", "Harper", "Riley", "Saylor", "Saylor", "Blaze", "Palmer", "Jane"]
    # for i in range(connt_record):
    #     random_record = Record(f"{rand_name[randint(0,10)]}",
    #                            f"{randint(1, 28)}.{randint(1, 12)}.{randint(1970, 2000)}")
    #     random_record.add_phone("".join([str(randint(0,9)) for _ in range(10)]))
    #     book.add_record(random_record)

    # Виведення всіх записів у книзі по 7 записів    
    # for text in book.iterator(7):
    #     print(text)
    #    input(WAIT_FOR_ENTER)
    
    # виводить список користувачів, які мають в імені
    #  або номері телефону є збіги із введеним рядком
    print(book.find_by_string("an"))

    book.save_to_file()

