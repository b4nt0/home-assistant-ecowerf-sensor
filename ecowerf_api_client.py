import logging
import requests
from datetime import date, datetime, timedelta


logger = logging.getLogger(__name__)

class EcowerfTokenError(RuntimeError):
    pass


class GarbageCollectorAPI:
    def __init__(self, garbage_token_url, garbage_consumer, garbage_secret, garbage_schedule_url):
        self.token = None
        self.garbage_token_url = garbage_token_url
        self.garbage_consumer = garbage_consumer
        self.garbage_secret = garbage_secret
        self.garbage_schedule_url = garbage_schedule_url

    def get_token(self):
        token_r = requests.get(self.garbage_token_url, headers={
            'x-consumer': self.garbage_consumer,
            'x-secret': self.garbage_secret
        })

        try:
            self.token = str(token_r.json()['accessToken'])
        finally:
            token_r.close()
            del token_r

        return self.token

    def get_schedule(self):
        result = []

        if False and self.token is None:
            try:
                self.get_token()
            except Exception:
                raise EcowerfTokenError()

        dt_start = date.today()
        dt_end = dt_start + timedelta(days=1)
        url = self.garbage_schedule_url.format(dt_start=dt_start.isoformat(),
                                             dt_end=dt_end.isoformat())
        headers = {
                'x-consumer': self.garbage_consumer,
                'content-type': 'application/json',
                'accept': 'application/json',
                'User-Agent': 'curl/7.68.0'
                # 'Authorization': self.token
            }

        logger.debug(f'Sending request to {url} with parameters {headers}...')

        schedule_r = requests.get(
            url,
            headers=headers)

        try:
            logger.debug(f'Received a schedule response: {schedule_r}, {schedule_r.text}')

            schedule_json = schedule_r.json()
            for item in schedule_json['items']:
                if 'fraction' not in item: continue
                if 'name' not in item['fraction']: continue
                if 'nl' not in item['fraction']['name']: continue
                dt = datetime.fromisoformat(item['timestamp'])
                dt_format = dt.strftime('%A, %d %B')
                result.append({'type': item['fraction']['name']['nl'], 'date': dt, 'date_format': dt_format})

        finally:
            schedule_r.close()
            del schedule_r

        return result
