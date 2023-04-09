#!/bin/env python3

# Add unique_id to all (old format) template sensors in configuration.yaml

from ruamel.yaml import YAML
import sys
import uuid

if len(sys.argv) != 2:
    print(f"Only one argument, filename, is allowed. {len(sys.argv)} given")
    sys.exit(1)

yaml = YAML()
yaml.indent(offset=2, sequence=4)
yaml.preserve_quotes = True

ha_configuration_yaml = sys.argv[1]
with open(ha_configuration_yaml) as fd:
    ha_config = yaml.load(fd)
old_sensors = ha_config.get("sensor")
for sensor in old_sensors:
    if sensor.get("platform") != "template":
        continue
    ses = sensor.get("sensors")
    for se in (s for s in ses if not ses[s].get("unique_id")):
        ses[se]["unique_id"] = str(uuid.uuid4())
#yaml.dump(ha_config, sys.stdout)
with open(ha_configuration_yaml + "_new", mode='w') as fd:
    yaml.dump(ha_config, fd)



