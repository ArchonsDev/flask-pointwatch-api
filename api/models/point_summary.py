from dataclasses import dataclass
from typing import Optional

@dataclass
class PointSummary(object):
    valid_points: Optional[float] = 0.0
    pending_points: Optional[float] = 0.0
    invalid_points: Optional[float] = 0.0
    required_points: Optional[float] = 0.0

    @property
    def excess_points(self):
        return max(0, self.valid_points - self.required_points)
    
    @property
    def lacking_points(self):
        return max(0, self.required_points - self.valid_points)
