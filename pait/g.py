from pait.data import PaitData
from pait.model.config import Config

# In order to reduce the intrusion of pait to the application framework,
# pait conducts data interaction through PaitData and Config
pait_data: PaitData = PaitData()
config: Config = Config()
