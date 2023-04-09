#!/bin/env python3

# Convert old format template sensors to the new template format in configuration.
# - friendly_name will be added as attribute to the new format
# - value_template --> state
# Everything else will be moved as is to the new format

from ruamel.yaml import YAML
import sys
import uuid
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config_file")
parser.add_argument("-d", "--dry-run", action="store_true")
args = parser.parse_args()

yaml = YAML()
yaml.indent(offset=2, sequence=4)
yaml.preserve_quotes = True

ha_configuration_yaml = args.config_file
with open(ha_configuration_yaml) as fd:
    ha_config = yaml.load(fd)
old_sensors = ha_config.get("sensor")
new_sensors = ha_config.get("template", [])

for sensor in old_sensors[:]:
    if sensor.get("platform") != "template":
        continue
    ses = sensor.get("sensors")
    for se in ses:
        ses[se]["unique_id"] = ses[se].get("unique_id", str(uuid.uuid4()))
        new_sensor = {
            "name": se,
            "state": ses[se]['value_template'],
            "attributes": {
                "friendly_name": ses[se].get("friendly_name", se)
            }
        }
        del ses[se]["friendly_name"]
        del ses[se]["value_template"]
        new_sensor.update(ses[se])
        ha_config["template"].append({
            "sensors": [
                new_sensor
                ]
        })
    old_sensors.remove(sensor)

ha_config["template"] = new_sensors

if args.dry_run:
    yaml.dump(ha_config, sys.stdout)
    sys.exit(0)

with open(ha_configuration_yaml + "_new", mode='w') as fd:
    yaml.dump(ha_config, fd)



