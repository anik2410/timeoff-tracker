from timeoff_base import TimeOffBase

class VacationManager(TimeOffBase):
    def __init__(self):
        super().__init__(
            db_file="vacation.db",
            table_records="vac_records",
            table_allowance="vac_allowance"
        )
