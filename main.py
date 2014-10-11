import json
import os
import re
import urllib2
import webapp2
from PIL import Image, ImageDraw, ImageFont

class MainHandler(webapp2.RequestHandler):
    plugin_info = {
        "name": "Amazon product information"
    }
    def get(self):
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
                    self.create_rating_image(m.group(1))
                else:
                    self.response.write("Not found")
                    self.response.status = 404
        else:
            self.response.content_type = "application/json"
            self.response.write(json.dumps(self.plugin_info))

    def create_rating_image(self, rating):
        img = Image.open("rating_background.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Roboto-Bold.ttf", 20)
        draw.text((30, 0), rating + " out of 5", (255, 0, 0), font=font)
        self.response.content_type = "image/png"
        img.save(self.response, "PNG")


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
