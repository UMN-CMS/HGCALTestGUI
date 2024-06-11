from PythonFiles.GUIConfig import GUIConfig


def update_config(full_id):

    if full_id[3] == 'W':
        from TestConfigs.Wagon_cfg import masterCfg
        print('Changed board config to Wagon')
        board_cfg = masterCfg

    if full_id[3] == 'E':
        from TestConfigs.Engine_cfg import masterCfg
        print('Changed board config to Engine')
        board_cfg = masterCfg

    else:
        from TestConfigs.Wagon_cfg import masterCfg
        print('Changed board config to Wagon')
        board_cfg = masterCfg

    return GUIConfig(board_cfg)
