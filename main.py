import json
import os
import re
import urllib2
import datetime
import webapp2
from PIL import Image, ImageDraw, ImageFont


PLUGIN_INFO = {
    "name": "Amazon product information"
}

# cache for 2 days
EXPIRATION_IN_SECONDS = 2 * 24 * 60 * 60
rating_font = ImageFont.truetype("Roboto-Bold.ttf", 18)
rating_footer_font = ImageFont.truetype("Roboto-Bold.ttf", 9)



class GMT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=10)

    def tzname(self, dt):
        return "GMT"

    def dst(self, dt):
        return datetime.timedelta(0)


def get_expiration_stamp(seconds):
    gmt = GMT()
    delta = datetime.timedelta(seconds=seconds)
    expiration = datetime.datetime.now()
    expiration = expiration.replace(tzinfo=gmt)
    expiration = expiration + delta
    return expiration.strftime("%a, %d %b %Y %H:%M:%S %Z")


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.set_default_headers()

        barcode = self.request.params.get("q", None)
        if barcode:
            url = "http://www.amazon.com/s/ref=nb_sb_noss?field-keywords=" + barcode
            open_details = self.request.params.get("d", None)
            if open_details:
                self.redirect(str(url))
            else:
                request = urllib2.Request(url, None, {'Referrer': 'http://shoppistant.com'})
                response = urllib2.urlopen(request)
                m = re.search("alt=\"(.*) out of 5 stars\"", response.read())
                if m:
                    self.send_rating_image(m.group(1))
                else:
                    self.response.write("Not found")
                    self.response.status = 404
        else:
            self.response.content_type = "application/json"
            self.response.write(json.dumps(PLUGIN_INFO))

    def set_default_headers(self):
        # allow CORS
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers["Expires"] = get_expiration_stamp(EXPIRATION_IN_SECONDS)
        self.response.headers["Content-Type"] = "application/json"
        self.response.headers["Cache-Control"] = "public, max-age=%d" % EXPIRATION_IN_SECONDS

    def send_rating_image(self, rating):
        rating="4.6"
        img = Image.open("rating_background.png")
        draw = ImageDraw.Draw(img)
        w, _ = draw.textsize(rating)
        draw.text((23 - w/2, 4), rating, (250, 153, 26), font=rating_font)
        draw.text((20, 25), "of 5", (225, 129, 37), font=rating_footer_font)
        self.response.content_type = "image/png"
        img.save(self.response, "PNG")


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
