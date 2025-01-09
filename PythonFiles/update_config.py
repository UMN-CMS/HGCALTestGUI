from PythonFiles.GUIConfig import GUIConfig
import yaml
from pathlib import Path
import os


ENV_NAME="GUI_CONFIG_PATH"
DEFAULT_PATH="/etc/HGCALTestGUI"

def loadConfig(cfg_type):
    p = Path(os.environ.get(ENV_NAME, DEFAULT_PATH))
    if not p.exists():
        p = Path(__file__).parent.parent / "Configs"
    with open(p / f"{cfg_type}_cfg.yaml", 'r') as f:
        ret = import_yaml(f)
    return ret

def update_config(full_id):
    if full_id[3:5] == 'WW' or full_id[3:5] == 'WE':
        cfg_type =  "LD_Wagon"
    elif full_id[3:5] == 'WH':
        cfg_type =  "HD_Wagon"
    elif full_id[3:5] == 'ZP':
        cfg_type =  "Zipper"
    elif full_id[3:5] == 'EL':
        cfg_type =  "LD_Engine"
    elif full_id[3:5] == 'EH':
        cfg_type =  "HD_Engine"
    else:
        cfg_type =  "LD_Wagon"
    board_cfg = loadConfig(cfg_type)
    return GUIConfig(board_cfg)

def import_yaml(filename):
    return yaml.safe_load(filename) 
