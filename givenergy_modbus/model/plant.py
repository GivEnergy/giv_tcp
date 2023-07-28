from typing import List

from pydantic import BaseModel

from givenergy_modbus.model.battery import Battery
from givenergy_modbus.model.inverter import Inverter, Inverter_AC  # type: ignore  # shut up mypy
from givenergy_modbus.model.register_cache import RegisterCache, RegisterCache_AC


class Plant(BaseModel):
    """Representation of a complete GivEnergy plant."""

    inverter_rc: RegisterCache
    inverter_rc_ac: RegisterCache_AC
    batteries_rcs: List[RegisterCache]

    class Config:  # noqa: D106
        arbitrary_types_allowed = True
        orm_mode = True
        # allow_mutation = False

    def __init__(self, **data):
        """Constructor. Use `number_batteries` to specify the total number of batteries installed."""
        data['inverter_rc'] = data.get('inverter_rc', RegisterCache())
        data['inverter_rc_ac'] = data.get('inverter_rc_ac', RegisterCache_AC())
        data['batteries_rcs'] = data.get(
            'batteries_rcs', [RegisterCache() for _ in range(data.get('number_batteries', 0))]
        )
        super().__init__(**data)

    @property
    def inverter(self) -> Inverter:
        """Return Inverter model for the Plant."""
        if self.inverter_rc:
            return Inverter.from_orm(self.inverter_rc)
        else:
            return Inverter_AC.from_orm(self.inverter_rc_ac)

    @property
    def batteries(self) -> List[Battery]:
        """Return Battery models for the Plant."""
        return [Battery.from_orm(rc) for rc in self.batteries_rcs]
