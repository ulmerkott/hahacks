#!/bin/env python3

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

import sys
import uuid
import argparse
from dataclasses import dataclass

parser = argparse.ArgumentParser(description="""
Convert old format template sensors to the new template format in configuration.
Friendly_name will be added as attribute to the new format.
- "value_template" will be converted to "state".
- "icon_template" will be converted to "icon".
Everything else will be moved as is to the new format.
""")
parser.add_argument("config_file")
parser.add_argument("-d", "--dry-run", action="store_true")

@dataclass
class LegacyTemplateSensorConverter():
    sensor: CommentedMap

    # Map of attributes of which name has changed in the new format.
    ATTR_NAME_CONVERSION_TABLE = {
        "value_template": "state",
        "icon_template": "icon"
    }

    def new_sensor(self):
        new_sensors = []
        ses = self.sensor.get("sensors")
        for sensor_name in ses:
            ses[sensor_name]["unique_id"] = ses[sensor_name].get("unique_id", str(uuid.uuid4()))
            new_sensor = {
                "name": sensor_name,
                "attributes": {
                    "friendly_name": sensor_name
                }
            }
            if friendly_name := ses[sensor_name].get("friendly_name"):
                new_sensor["attributes"]["friendly_name"] = friendly_name
                del ses[sensor_name]["friendly_name"]

            for old_attr, new_attr in self.ATTR_NAME_CONVERSION_TABLE.items():
                if attr := ses[sensor_name].get(old_attr):
                    new_sensor[new_attr] = attr
                    del ses[sensor_name][old_attr]

            new_sensor.update(ses[sensor_name])
            new_sensors.append({
                "sensor": [
                    new_sensor
                    ]
            })

        return new_sensors


def main():
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
        new_sensors += LegacyTemplateSensorConverter(sensor).new_sensor()
        old_sensors.remove(sensor)

    ha_config["template"] = new_sensors

    if args.dry_run:
        yaml.dump(ha_config, sys.stdout)
        sys.exit(0)

    new_config_file = ha_configuration_yaml + "_new"
    with open(new_config_file, mode='w') as fd:
        yaml.dump(ha_config, fd)
        print(f"Create new configuration file: {new_config_file}")

if __name__ == "__main__":
    main()


