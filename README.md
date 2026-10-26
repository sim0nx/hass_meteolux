# MeteoLux

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Validate](https://github.com/sim0nx/hass_meteolux/actions/workflows/validate.yml/badge.svg)](https://github.com/sim0nx/hass_meteolux/actions/workflows/validate.yml)

<img src="custom_components/hass_meteolux/brand/icon.png" alt="MeteoLux logo" width="128">

Home Assistant integration for the weather forecasts of
[MeteoLux](https://www.meteolux.lu), the national weather service of
Luxembourg. It uses the public MeteoLux API through
[python-meteolux](https://github.com/sim0nx/python-meteolux).

## Installation

Add this repository as a custom repository in HACS, or copy
`custom_components/hass_meteolux` into your Home Assistant
`config/custom_components` folder. Requires Home Assistant 2025.3 or newer;
the integration logo is shown from Home Assistant 2026.3 onwards.

## Configuration

Add the integration from **Settings → Devices & services** and pick one of
the places MeteoLux publishes forecasts for. Add the integration again for
more places.

## Entities

Each place gets a weather entity with the current conditions, an hourly
forecast (in 6-hour periods) and a daily forecast, and sensors for
temperature, humidity, pressure and wind speed. Only the humidity sensor is
enabled by default.

Forecast values given as a range (for example wind of 20-30 km/h) use the
upper bound. Humidity, pressure and visibility are measured at the
Luxembourg Findel airport station, the only station in the API, and are the
same for every place. Data is refreshed every 15 minutes.

The meaning of the MeteoLux weather icons is documented in
[README_api.md](README_api.md).

## Development

```bash
pip install -r requirements_test.txt
pytest
```

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
