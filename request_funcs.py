import requests


def get_localoties(
        api_key: str,
        name_beginning: str
) -> list[list] | None:
    try:
        response = requests.get(
            'http://dataservice.accuweather.com/locations/v1/cities/autocomplete',
            params={
                'apikey': api_key,
                'q': name_beginning,
                'language': 'ru'
            }
        )
    except requests.exceptions.ConnectionError:
        return
    if response.ok:
        return sorted(
            (
                [
                    location['Country']['LocalizedName'],
                    location['AdministrativeArea']['LocalizedName'],
                    location['LocalizedName'],
                    location['Key']
                ]
                for location in response.json()
            ),
            key=lambda t: t[:3]
        )  # сортируем сначала по стране, затем по региону, затем по названию НП


def get_weather(
        api_key: str,
        location_key: int,
        round_values: bool = True
) -> tuple[float | int, float, float]:
    try:
        response = requests.get(
            f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}",
            params={'apikey': api_key, 'details': True}
        )
    except requests.exceptions.ConnectionError:
        return
    if response.ok:
        data = response.json()
        rain_probability: float | int = data['DailyForecasts'][0]['Day']['RainProbability']  # в процентах
        # region Скорость ветра в км/ч
        # формулу взял отсюда http://www.for6cl.uznateshe.ru/wp-content/uploads/2018/04/kilometry-v-mili.png
        wind_speed = data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']  # в mi/h
        wind_speed = wind_speed * 15_625 / 25_146  # в км/ч
        # endregion
        # region Средняя температура в °C
        mean_temperature: float = (
                    data['DailyForecasts'][0]['Temperature']['Maximum']['Value'] +
                    data['DailyForecasts'][0]['Temperature']['Minimum']['Value']
                ) / 2  # в Фаренгейтах
        mean_temperature: float = 5 * (mean_temperature - 32) / 9
        # endregion

        if round_values:
            rain_probability = round(rain_probability, 2)
            wind_speed = round(wind_speed, 2)
            mean_temperature = round(mean_temperature, 2)
        return rain_probability, wind_speed, mean_temperature
