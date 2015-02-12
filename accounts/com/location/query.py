import urllib, json

class locationQuery:

    status = None
    results = None
    formatted_address = None

    def __init__(self):
        pass

    def query(self, location):
        if location is None or location is "":
            return

        url_data = location.replace(" ", "+")  # Encode the URL all special like
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + url_data

        le_data = urllib.request.urlopen(url)
        resp_data = json.loads(str(le_data.read().decode("utf-8")))

        import pprint
        pprint.pprint(resp_data)

        if resp_data['status'] == 'ZERO_RESULTS' or 'partial_match' in resp_data['results'][0] or resp_data['status'] != "OK":
            self.status = False
            self.results = (0, 0)
        else:
            self.status = True
            self.results = (resp_data['results'][0]['geometry']['location']['lat'],
                            resp_data['results'][0]['geometry']['location']['lng'])
            self.formatted_address = resp_data['results'][0]['formatted_address']

    def tostring(self):
        return str(self.results[0])+","+str(self.results[1])