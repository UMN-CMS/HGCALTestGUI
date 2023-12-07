from PythonFiles.GUIConfig import GUIConfig
import yaml
from pathlib import Path


def update_config(sn):

    if sn[3] == 'W':
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/Wagon_cfg.yaml"))
        print(masterCfg)
        print('Changed board config to Wagon')
        board_cfg = masterCfg

    if sn[3] == 'E':
        #from TestConfigs.Engine_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/Engine_cfg.yaml"))
        print('Changed board config to Engine')
        board_cfg = masterCfg

    else:
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/Wagon_cfg.yaml"))
        print(masterCfg)
        print('Changed board config to Wagon')
        board_cfg = masterCfg

    return GUIConfig(board_cfg)

def import_yaml(filename):

    return yaml.safe_load(filename) 
