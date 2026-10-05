import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.import_employees as importer
from scripts.import_employees import (
    _parse_birthday,
    _parse_joining_date,
    import_employees,
)


class ImportEmployeeTests(unittest.TestCase):
    def test_birthday_has_no_year_and_supports_february_29(self):
        self.assertEqual(_parse_birthday("28 July", 2), (7, 28))
        self.assertEqual(_parse_birthday("29 February", 2), (2, 29))

    def test_joining_date_requires_a_full_date(self):
        self.assertEqual(
            _parse_joining_date("15 March 2022", 2).isoformat(),
            "2022-03-15",
        )
        with self.assertRaises(ValueError):
            _parse_joining_date("15 March", 2)

    def test_dry_run_validates_csv_without_supabase_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "employees.csv"
            path.write_text(
                "employee_id,name,date_of_joining,birthday\n"
                "EMP001,Asha,15 March 2022,28 July\n",
                encoding="utf-8",
            )
            self.assertEqual(
                import_employees(path, dry_run=True),
                {"rows": 1, "created": 0, "updated": 0},
            )

    def test_import_uses_month_day_and_upserts_both_events(self):
        class FakeClient:
            def __init__(self):
                self.person = None
                self.events = []

            def object_exists(self, *_):
                return True

            def person_by_employee_id(self, _):
                return self.person

            def upsert_person(self, values):
                self.person = {"id": "person-1", **values}
                return self.person

            def upsert_event(self, values):
                self.events.append(values)
                return values

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "employees.csv"
            path.write_text(
                "employee_id,name,date_of_joining,birthday\n"
                "EMP001,Asha,15 March 2022,29 February\n",
                encoding="utf-8",
            )
            fake = FakeClient()
            with patch.object(importer, "_client", return_value=fake):
                first = import_employees(path)
                second = import_employees(path)

        self.assertEqual(first["created"], 1)
        self.assertEqual(second["updated"], 1)
        birthday = fake.events[0]
        self.assertIsNone(birthday["event_date"])
        self.assertEqual((birthday["event_month"], birthday["event_day"]), (2, 29))
        anniversary = fake.events[1]
        self.assertEqual(anniversary["event_date"], "2022-03-15")


if __name__ == "__main__":
    unittest.main()
