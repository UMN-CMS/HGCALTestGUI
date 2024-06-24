import yaml

from glob import glob

def dump_to_yaml(mastercfg):

    yaml_string = yaml.dump(mastercfg)


    with open("temp.yaml", "w") as f:

        f.write(yaml_string)

    f.close()



