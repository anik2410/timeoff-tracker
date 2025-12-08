from timeoff_base import TimeOffBase

class PersonalManager(TimeOffBase):
    def __init__(self):
        super().__init__(
            db_file="personal.db",
            table_records="per_records",
            table_allowance="per_allowance"
        )
