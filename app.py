import flask
from request_funcs import get_localoties, get_weather


api_key = input("Введите API-ключ: ")

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def location_input_page():
    return flask.render_template('location_input.html')


@app.route('/location_choice', methods=['POST'])
def location_choice_page():
    data = []
    for arg_name in ('p1', 'p2'):
        localoties = get_localoties(api_key=api_key, name_beginning=flask.request.form[arg_name])
        if localoties is None:
            return flask.render_template('mistake_of_request.html')
        data.append(localoties)
        # region Нумеруем
        for n, location in enumerate(data[-1], start=1):
            location.insert(0, n)
        # endregion
        data[-1] = tuple(map(tuple, data[-1]))  # преобразовываем к кортежу кортежей
    if all(data):  # если по введённым пользователем названиям нашлись НП
        return flask.render_template(
            'location_choice.html',
            data1=data[0],
            max1=len(data[0]),
            data2=data[1],
            max2=len(data[1])
        )
    else:
        return flask.render_template('mistake_of_input.html')


def check_good_weather(
        mean_temperature,
        wind_speed,
        rain_probability
):
    """Сделано согласно заданию"""
    return \
        0 <= mean_temperature <= 35 and \
        wind_speed <= 50 and \
        rain_probability <= 70


@app.route('/weather/<data1>&<data2>', methods=['POST'])
def weather_page(data1, data2):
    p1_n = int(flask.request.form["p1_n"])
    p2_n = int(flask.request.form["p1_n"])

    location1 = list(eval(data1)[p1_n-1])
    location2 = list(eval(data2)[p2_n-1])
    del data1, data2, location1[0], location2[0]

    if location1[3] == location2[3]:
        return flask.render_template('mistake_locs_are_same.html')

    weather1 = get_weather(api_key=api_key, location_key=location1[3])
    if weather1 is None:
        return flask.render_template('mistake_of_request.html')
    rain_probability_1, wind_speed_1, mean_temperature_1 = weather1
    weather2 = get_weather(api_key=api_key, location_key=location2[3])
    if weather2 is None:
        return flask.render_template('mistake_of_request.html')
    rain_probability_2, wind_speed_2, mean_temperature_2 = weather2
    del weather1, weather2
    weather_status_1: bool = check_good_weather(
        mean_temperature=mean_temperature_1,
        wind_speed=wind_speed_1,
        rain_probability=rain_probability_1
    )
    weather_status_2: bool = check_good_weather(
        mean_temperature=mean_temperature_2,
        wind_speed=wind_speed_2,
        rain_probability=rain_probability_2
    )

    return flask.render_template(
        'weather.html',

        # общая информация
        country1=location1[0],
        country2=location2[0],
        region1=location1[1],
        region2=location2[1],
        name1=location1[2],
        name2=location2[2],

        # информация о погоде
        rain_probability_1=rain_probability_1,
        wind_speed_1=wind_speed_1,
        mean_temperature_1=mean_temperature_1,
        rain_probability_2=rain_probability_2,
        wind_speed_2=wind_speed_2,
        mean_temperature_2=mean_temperature_2,
        weather_status_1=('Ой-ой, погода плохая', 'Погода — супер')[weather_status_1],
        weather_status_2=('Ой-ой, погода плохая', 'Погода — супер')[weather_status_2],

        common_weather_status=('Ой-ой, погода плохая', 'Погода — супер')[weather_status_1 and weather_status_2]
    )


if __name__ == '__main__':
    app.run(debug=True)
