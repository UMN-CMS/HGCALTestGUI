from PythonFiles.GUIConfig import GUIConfig
import yaml
from pathlib import Path
import os

# TODO change this so it loads the correct config file based on the board

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
    if full_id[3:5] == 'WM':
        cfg_type =  "WM"
    board_cfg = loadConfig(cfg_type)
    return GUIConfig(board_cfg)

def import_yaml(filename):
    return yaml.safe_load(filename) 
