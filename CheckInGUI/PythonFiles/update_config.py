from PythonFiles.GUIConfig import GUIConfig
import yaml
from pathlib import Path


def update_config(full_id):

    # sets the config to wagon or engine based on the 4th character of the board's full id
    if full_id[3] in ('Z', 'W'):
        #from TestConfigs.Wagon_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/Wagon_cfg.yaml"))
        print(masterCfg)
        print('Changed board config to Wagon')
        board_cfg = masterCfg

    if full_id[3] == 'E':
        #from TestConfigs.Engine_cfg import masterCfg
        masterCfg = import_yaml(open(Path(__file__).parent.parent / "Configs/Engine_cfg.yaml"))
        print(masterCfg)
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
