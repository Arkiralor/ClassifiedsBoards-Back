from classifieds_app.helpers import ClassifiedsCategoryHelper
from secrets import token_hex
from faker import Faker

fake = Faker(locale='en_US',
             )

def main():
    for _ in range(1024):
        data = {
            "name": f"{' '.join(fake.words())}",
            "description": f"{fake.text(max_nb_chars=200)}",
        }

        _ = ClassifiedsCategoryHelper.create(data=data)

if __name__ == "__main__":
    main()