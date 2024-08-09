from PythonFiles.GUIConfig import GUIConfig
import yaml
from pathlib import Path


def update_config(full_id):

    # sets the config to wagon or engine based on the 4th character of the board's full id
    if full_id[3:5] == 'WW' or full_id[3:5] == 'WE':
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/LD_Wagon_cfg.yaml"))
        board_cfg = masterCfg

    if full_id[3:5] == 'WH':
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/HD_Wagon_cfg.yaml"))
        board_cfg = masterCfg

    if full_id[3:5] == 'EL':
        #from TestConfigs.Engine_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/LD_Engine_cfg.yaml"))
        board_cfg = masterCfg

    if full_id[3:5] == 'EH':
        #from TestConfigs.Engine_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/HD_Engine_cfg.yaml"))
        board_cfg = masterCfg

    else:
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/LD_Wagon_cfg.yaml"))
        board_cfg = masterCfg

    return GUIConfig(board_cfg)

def import_yaml(filename):

    return yaml.safe_load(filename) 
