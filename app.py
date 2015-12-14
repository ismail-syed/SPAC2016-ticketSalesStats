import os

import eventbrite
from flask import Flask, render_template, request
import pusher

# We fetch our constants by taking them from environment variables
#   defined in the .env file.
EVENTBRITE_EVENT_ID = os.environ['EVENTBRITE_EVENT_ID']
EVENTBRITE_OAUTH_TOKEN= os.environ['EVENTBRITE_OAUTH_TOKEN']
PUSHER_APP_ID = os.environ['PUSHER_APP_ID']
PUSHER_KEY = os.environ['PUSHER_KEY']
PUSHER_SECRET = os.environ['PUSHER_SECRET']

# Instantiate the Eventbrite API client.
eventbrite = eventbrite.Eventbrite(EVENTBRITE_OAUTH_TOKEN)

# Instantiate the pusher object. This library is used to push actions
#   to the browser when they occur.
p = pusher.Pusher(app_id=PUSHER_APP_ID, key=PUSHER_KEY, secret=PUSHER_SECRET)

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    """ This is the display view. """

    # Get the event details
    event = eventbrite.get_event(EVENTBRITE_EVENT_ID, expand='ticket_classes')

    # Get the attendee list
    attendees = eventbrite.get_event_attendees(EVENTBRITE_EVENT_ID)

    # Reverse so latest to sign up is at the top
    attendees['attendees'].reverse()

    ticketClasses = eventbrite.get('/events/' + EVENTBRITE_EVENT_ID + '/ticket_classes/')


    # Render our HTML.
    return render_template(
        'index.html',
        settings={'PUSHER_KEY': PUSHER_KEY},
        event=event,
        attendees=attendees
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    """
        Webhooks simply provide API endpoints that the user can use to gather
        more information. They are sent as HTTP POSTS with the JSON mimetype
        specified in the header.

    """

    # Use the API client to convert from a webhook to an API object. An API
    #   object is just a Python dict with some extra methods.
    api_object = eventbrite.webhook_to_object(request)

    # Use pusher to add content to to the HTML page.
    p['webhooks'].trigger("Attendee", api_object)
    p['webhooks'].trigger("Event", event)
    return ""


if __name__ == '__main__':
    app.run()