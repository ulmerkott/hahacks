from convert_to_new_template_format import main

import yaml
import sys


old_format_config_yaml = """
sensor:
  - platform: template
    sensors:
      partikelsensor_pm2_5:
        friendly_name: 'PM2.5 air quality sensor'
        unit_of_measurement: 'µg/m³'
        value_template: "{{- 666 -}}"
        icon_template: mdi:air-filter
        unique_id: edb3577d-90cd-4604-8f1c-6c77785c36c7
  - platform: template
    sensors:
      partikelsensor_pm10:
        friendly_name: 'PM2.5 air quality sensor'
        unit_of_measurement: 'µg/m³'
        value_template: "{{- 555 -}}"
        icon_template: mdi:air-filter
"""

def test_convert_to_new_format(tmpdir, capsys):
    config_file = f"{tmpdir}/configuration.yaml"
    open(config_file, "w").write(old_format_config_yaml)
    sys.argv += [config_file]
    main()

    old_config = {}
    with open(config_file) as f:
        old_config = yaml.safe_load(f)

    with open(config_file + "_new") as f:
        new_config = yaml.safe_load(f)
        # Test name creation
        assert new_config["template"][0]["sensor"][0]["name"] == \
            list(old_config["sensor"][0]["sensors"].keys())[0]

        assert new_config["template"][1]["sensor"][0]["name"] == \
            list(old_config["sensor"][1]["sensors"].keys())[0]

