from brutal.core.plugin import BotPlugin, threaded, cmd
from brutal.core.util import split_args_by
import requests
import datetime
from pygeocoder import Geocoder

DATE_FORMAT = '%d.%m.%Y'


def get_json_or_timeout(url):
    """Return json data (or None on timeout) grabbed from
       service given in argument"""
    try:
        r = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        return None
    return r.json()


class WeatherError(Exception):
    def __init__(self, detail):
        self.detail = detail

    def __str__(self):
        return str(self.detail)


class Wunderground:
    def __init__(self, apikey, country, lang):
        self.APIKEY = apikey
        self._features = ['conditions', 'forecast10day']
        self.lang = lang
        self.api_url = 'http://api.wunderground.com/api/{0}/' \
                       '{1}/lang:{2}/q/{3}.json'
        self.country = country

    def retrieve(self, city, attempt=1):
        """Try to grab json data in multiple ways"""
        r = get_json_or_timeout(self.api_url.format(self.APIKEY,
                                                    '/'.join(self._features),
                                                    self.lang,
                                                    city))

        # when service is unreachable or times out
        if r is None:
            raise WeatherError('Could not reach wunderground.com')
        # if service does not recognize city, it returns possible
        # zmw code, which is possible to search for city with
        elif 'results' in r['response']:
            return self.retrieve('zmw:' + r['response']['results'][0]['zmw'],
                                 attempt + 1)
        # some cities are not recognized and have to have `,country` at the end
        # or be searched based on latitude and longitude
        elif 'error' in r['response']:
            if attempt < 2:
                loc = Geocoder.geocode(city)
                return self.retrieve(','.join([str(loc[0].latitude),
                                               str(loc[0].longitude)]),
                                     attempt + 1)
            elif attempt < 3:
                return self.retrieve(city + ',' + self.country, attempt + 1)
            raise WeatherError(r['response']['error']['description'])
        else:
            return r

    def output(self, r, daydiff, format_str):
        """Return formated data"""
        txt = r['forecast']['txt_forecast']['forecastday']
        txt = txt[(daydiff + 1) * 2]['fcttext_metric']

        forecastday = r['forecast']['simpleforecast']['forecastday']
        daytemp = forecastday[daydiff + 1]['high']['celsius']
        nighttemp = forecastday[daydiff + 1]['low']['celsius']
        avewind = str(forecastday[daydiff + 1]['avewind']['kph'])
        city = r['current_observation']['display_location']['city']

        data = {'city': city, 'daytemp': daytemp, 'nighttemp': nighttemp,
                'avewind': avewind, 'txt': txt}
        return format_str.format(**data)


class Weather(BotPlugin):
    def setup(self, *args, **kwargs):
        if 'APIKEY' in self.config:
            self.APIKEY = self.config['APIKEY']
        else:
            raise WeatherError('No `APIKEY` specified in config file')
        self._provider = Wunderground(self.APIKEY, 'Slovakia', 'EN')

    @threaded
    @cmd
    def weather(self, event):
        """Check for weather in given location

        Examples:
            !weather Bratislava
            !weather Bratislava - 20.12.2014
        """
        args = event.args

        if not len(args):
            return

        if '-' in args:
            args = split_args_by(args, '-')

        try:
            # try to grab last argument, which can be date
            # and squash other ones into destination
            date = datetime.datetime.strptime(args[-1], DATE_FORMAT)
            dest = ' '.join(args[:-1])
        except:
            # if there is not date at the end, just use current one
            # and squash all the arguments into destination
            date = datetime.datetime.today()
            dest = ' '.join(args)

        curr_date = datetime.datetime.today()
        diff = (date - curr_date).days

        try:
            data = self._provider.retrieve(dest)
            fill = u'{city} -> Day: {daytemp}\u2103 ' \
                   u', Night: {nighttemp}\u2103 ' \
                   ', Wind: {avewind} km/h ({txt})'
            return self._provider.output(data, diff, fill).encode('utf-8')
        except WeatherError as e:
            return str(e).encode('utf-8')
