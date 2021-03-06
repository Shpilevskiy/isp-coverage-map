import unittest


from by_isp_coverage.connection import Connection
from by_isp_coverage.validators import ConnectionValidator, Toponym


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.validator = ConnectionValidator()

    def create_connection(self, region="test", city="test",
                          street="test", provider="test",
                          house="1", status=""):
        return Connection(region=region, city=city, street=street,
                          provider=provider, house=house, status=status)


class TestCityValidation(BaseCase):

    def test_correctly_format_city_remains_the_same(self):
        city = "Сенница"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(city, validated)

    def test_single_word_uppercase_city_transformed_correctly(self):
        city = "СЕННИЦА"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Сенница")

    def test_multiple_word_uppercase_city_transformed_correctly(self):
        city = "СЕННИЦА БОЛЬШАЯ"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Сенница Большая")

    def test_removes_abbreviations(self):
        options = [
            ('Хотимск г.п.', 'Хотимск'),
            ('Шклов г.', 'Шклов'),
            ('Межисятки аг.', 'Межисятки'),
            ('Вязынь д.', 'Вязынь'),
            ('Мачулищи п.г.т', 'Мачулищи'),
            ('д. Сосновая', 'Сосновая'),
            ('Нарочь к.', 'Нарочь'),
            ('Жемчужный агр.', 'Жемчужный'),
        ]
        for opt in options:
            validated = self.validator.validate_city_field(opt[0])[0]
            self.assertEqual(validated, opt[1])

    def test_converts_to_correct_case_with_abbreviations(self):
        options = [
            ('ХОТИМСК г.п.', 'Хотимск'),
            ('МЕЖИСЯТКИ МЕЖДУНАРОДНЫЕ аг.', 'Межисятки Международные'),
            ('д. СОСНОВАЯ', 'Сосновая'),
        ]
        for opt in options:
            validated = self.validator.validate_city_field(opt[0])[0]
            self.assertEqual(validated, opt[1])

    def test_extra_cases(self):
        city = "САМОХВАЛОВИЧИ п"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Самохваловичи")

    def test_city_connections_validated(self):
        options = [
            ('ХОТИМСК г.п.', 'Хотимск'),
            ('МЕЖИСЯТКИ МЕЖДУНАРОДНЫЕ аг.', 'Межисятки Международные'),
            ('д. СОСНОВАЯ', 'Сосновая'),
        ]
        expected_result = [self.create_connection(city=o[1]) for o in options]
        test_data = [self.create_connection(city=o[0]) for o in options]
        self.assertEqual(list(self.validator._validate_city(test_data)),
                         expected_result)


class TestHouseValidation(BaseCase):

    def test_simple_connection_returned_as_is(self):
        connections = [self.create_connection(house="20")]
        result = list(self.validator._validate_house(connections))
        self.assertEqual(result, connections)

    def test_list_with_digital_numbers_wo_spaces_processed_correctly(self):
        # If multiple houses are specified new connections should be built
        connections = [self.create_connection(house="20,30,40")]
        result = list(self.validator._validate_house(connections))

        expected_result = [self.create_connection(house=str(i))
                           for i in (20, 30, 40)]
        self.assertEqual(expected_result, result)

    def test_list_with_digital_numbers_wo_spaces_ending_with_comma_processed_correctly(self):
        connections = [self.create_connection(house="20,30,40,")]
        result = list(self.validator._validate_house(connections))

        expected_result = [self.create_connection(house=str(i))
                           for i in (20, 30, 40)]
        self.assertEqual(expected_result, result)

    def test_list_with_digital_numbers_with_spaces_processed_correctly(self):
        connections = [self.create_connection(house="20,30, 40")]
        result = list(self.validator._validate_house(connections))

        expected_result = [self.create_connection(house=str(i))
                           for i in (20, 30, 40)]
        self.assertEqual(expected_result, result)


class TestBuildingNumberValidations(BaseCase):

    def test_decimal_building_number_parsed_correctly(self):
        connections = [self.create_connection(house="29")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="29")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_parsed_correctly(self):
        connections = [self.create_connection(house="29А")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="29А")]
        self.assertEqual(result, expected_result)

    def test_building_number_with_letter_uppercased(self):
        connections = [self.create_connection(house="29а")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="29А")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_dash_parsed_correctly(self):
        connections = [self.create_connection(house="29/1")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="29/1")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_letter_parsed_correctly(self):
        connections = [self.create_connection(house="8 к.4")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="8 (корпус 4)")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_spaced_letter_parsed_correctly(self):
        connections = [self.create_connection(house="8 к4")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="8 (корпус 4)")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_space_parsed_correctly(self):
        connections = [self.create_connection(house="8 Б")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="8Б")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_hyphen_parsed_correctly(self):
        connections = [self.create_connection(house="8-2")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="8-2")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_letter_and_comma_parsed_correctly(self):
        connections = [self.create_connection(house="119, к.1")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="119 (корпус 1)")]
        self.assertEqual(result, expected_result)

    def test_building_numbers_with_space_and_formatted(self):
        connections = [self.create_connection(house="56а корпус 1")]
        result = list(self.validator._validate_house(connections))
        expected_result = [self.create_connection(house="56А (корпус 1)")]
        self.assertEqual(result, expected_result)


class TestArtificialPeopleValidation(BaseCase):

    def test_artificial_person_simple_upper(self):
        test_c = self.create_connection(house="2 ЮР. ЛИЦА", status="Here I am")
        validated = list(self.validator._validate_house([test_c]))
        expected_result = self.create_connection(house="2", status="Here I am (юридические лица)")
        self.assertEqual(validated, [expected_result])


class TestToponymsParsing(BaseCase):

    def test_simple_street_name_parsed(self):
        test_s = 'улица Алибегова'
        t = Toponym(test_s)
        self.assertEqual(t._original_str, test_s)
        self.assertEqual(t.type, 'улица')
        self.assertEqual(t.name, 'Алибегова')

    def test_toponym_post_validation(self):
        test_s = 'улица Я.Купалы'
        t = Toponym(test_s)
        self.assertEqual(t.name, 'Янки Купалы')

    def test_toponym_name_normalization(self):
        test_data = [
            ("ленина", "Ленина"),
            ("ЛЕНИНА", "Ленина"),
        ]
        for name, expected_name in test_data:
            self.assertEqual(Toponym._normalize_name(name), expected_name)

    def test_street_type_and_name_extracted(self):
        test_data = [
            ("ленина", None, "ленина"),
            ("ул. ленина", "улица", "ленина"),
            ("УЛ. ЛЕНИНА", "улица", "ЛЕНИНА"),
            ("УЛИЦА ЛЕНИНА", "улица", "ЛЕНИНА"),
            ("ЛЕНИНА УЛ.", "улица", "ЛЕНИНА"),

        ]
        for name, expected_type, expected_name in test_data:
            t = Toponym("")
            self.assertEqual(t._extract_type_and_name(name),
                             (expected_type, expected_name))

    def test_street_formatting(self):
        test_data = [
            "ленина", "ул. ленина", "УЛ. ЛЕНИНА",
            "УЛИЦА ЛЕНИНА", "улица Ленина", "ЛЕНИНА УЛ."
        ]
        correct_name = "улица Ленина"
        for name in test_data:
            t = Toponym(name, default_type="улица")
            self.assertEqual(t.format(), correct_name)

    def test_street_test_cases(self):
        # "1 переулок Урицкого" - кто вообще придумал такие названия!?
        test_data = [
            ("Ленина", "улица", "Ленина"),
            ("1 мая", "улица", "1 Мая"),
            ("28 Июля ул.", "улица", "28 Июля"),
            ("50 ЛЕТ ПОБЕДЫ УЛ.", "улица", "50 Лет Победы"),
            ("ул. Якубовского", "улица", "Якубовского"),
            ("ул. Ф.Скорины", "улица", "Ф.Скорины"),
            ("УЛ. АСОНАЛИЕВА", "улица", "Асоналиева"),
            ("УЛИЦА АСОНАЛИЕВА", "улица", "Асоналиева"),
            ("ХАРЬКОВСКАЯ УЛ.", "улица", "Харьковская"),
            ("Красноармейская Ул,", "улица", "Красноармейская"),
            ("Индустриальный Прз.", "проезд", "Индустриальный"),
            ("Звёздный Пр-Д", "проезд", "Звёздный"),
        ]
        for s, expected_type, expected_name in test_data:
            t = Toponym(s)
            self.assertEqual(t.type, expected_type)
            self.assertEqual(t.name, expected_name)

    def test_pre_validation_hook(self):
        replacement_map = {'тест': ('улица', 'новая тестовая')}
        c = self.create_connection(street="тест")
        v = ConnectionValidator(pre_replacement_street_map=replacement_map)
        validated = list(v.validate_connections([c]))
        self.assertEqual(validated[0].street, 'улица новая тестовая')

    def test_post_validation_hook(self):
        replacement_map = {'К. Маркса': 'Карла Маркса'}
        c = self.create_connection(street="к. маркса")
        v = ConnectionValidator(post_replacement_street_map=replacement_map)
        validated = list(v.validate_connections([c]))
        self.assertEqual(validated[0].street, 'улица Карла Маркса')
