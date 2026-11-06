# Data model for a cleaned scheme record.

from dataclasses import asdict, dataclass


@dataclass
class Record:
    scheme_name: str
    max_project_cost: str
    subsidy_general: str
    subsidy_special: str
    own_contribution: str
    eligibility: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
