"""swarmbasecore.agency_swarm_framework.swarmy_agency

This module defines the SwarmyAgency class, which extends the Agency class 
from the agency_swarm module. The SwarmyAgency class should serve as a wrapper 
for logging.
# TODO
"""

from agency_swarm import Agency


class SwarmyAgency(Agency):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
