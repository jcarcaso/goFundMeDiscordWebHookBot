from urllib.request import urlopen
import json
from discord_webhook import DiscordEmbed, DiscordWebhook
from datetime import datetime
from datetime import timedelta
import pytz
import constant

def build_url(base_url, offset, limit):
    return base_url + "?limit=" + str(limit) + \
            "&offset=" + str(offset) + "&" + \
            constant.DISCORD_SORT_URL_PARAM
    
def validate_event_params(event):
    validation_error = []

    # Validate required keys exist
    for key in [constant.INTERVAL_KEY, constant.DISCORD_KEY, constant.GFM_KEY]:
        if key not in event or not event[key]:
            validation_error.append("{} is not defined in your event parameters.".format(key))

    # Validate interval is a positive integer
    if constant.INTERVAL_KEY in event and (type(event[constant.INTERVAL_KEY]) is not int or 
                                            event[constant.INTERVAL_KEY] <= 0):
        validation_error.append("{} must be a positive integer for milliseconds".format(constant.INTERVAL_KEY))
    
    # If the offset isn't present use default and validate it is a number
    if constant.OFFSET_KEY not in event:    
        event[constant.OFFSET_KEY] = constant.OFFSET_DEFAULT 
    elif type(event[constant.OFFSET_KEY]) is not int or event[constant.OFFSET_KEY] <= 0:
        validation_error.append("{} must be a positive integer".format(constant.OFFSET_KEY))

    return validation_error
    
def lambda_handler(event, context):
    show_latest = 0 # Set to > 0 to test sending the latest X donations
    validation_error = validate_event_params(event)
    if len(validation_error) > 0:
        return {
            "statusCode": 500,
            "body": {"message": "\n".join(validation_error)}
        }

    now = datetime.now(pytz.UTC)
    # check for donations between last start/end interval 
    # Current assumption, the function runs on the minute of your scheduling interval
    start_interval = now.replace(second=0,microsecond=0) - \
                    timedelta(milliseconds=event[constant.INTERVAL_KEY])
    end_interval = now.replace(second=0,microsecond=0)
    cur_offset = 0

    description = ""
    done = False
    base_url = constant.GFM_BASE_URL.format(campaign=event[constant.GFM_KEY])

    while not done:
        response = urlopen(build_url(base_url, cur_offset, event[constant.OFFSET_KEY]))
        if response.status != 200:
            return {
                "statusCode": 500,
                "body": {"message": "Failed to retrive donations from endpoint {}".format(base_url)}
            }
        # increment the offset for subsequent calls if needed
        cur_offset += event[constant.OFFSET_KEY]
        data_json = json.loads(response.read())
        if "references" not in data_json or "donations" not in data_json["references"]:
            return {
                "statusCode": 500,
                "body": {"message": "Donations not found"}
            }
        donation_list = data_json["references"]["donations"]

        for donation in donation_list:
            # Get donation information
            name = donation["name"]
            amount = format(donation["amount"], ".2f")
            isAnonymous = donation["is_anonymous"]
            donationDate = datetime.strptime(donation["created_at"], "%Y-%m-%dT%H:%M:%S%z")
            if (donationDate >= start_interval and donationDate < end_interval) or show_latest>0:
                # If testing, decrement the counter in show_latest
                show_latest -= 1
                    
                minutes, seconds = divmod((now.replace(microsecond=0) - donationDate).total_seconds(), 60)
                minutesString = "" if minutes < 1 else \
                                " 1 minute" if minutes == 1 else \
                                " " + str(int(minutes)) + " minutes"
                secondsString = "" if seconds < 1 else \
                                " 1 second" if seconds == 1 else \
                                " " + str(int(seconds)) + " seconds"
                description = description + \
                                ("\n" if description else "") + \
                                ("An anonymous donator" if isAnonymous else name) + \
                                " donated $" + str(amount) + \
                                minutesString + \
                                (" and " if minutesString and secondsString else "") + \
                                secondsString + " ago"
            else:
                done = True
                break

    if description and show_latest < 0:
        webhook = DiscordWebhook(url=event[constant.DISCORD_KEY])
        
        embed = DiscordEmbed(
            title=constant.DISCORD_EMBED_TITLE,
            description=description,
            color=constant.DISCORD_EMBED_COLOR)

        webhook.add_embed(embed)
        webhook.execute()
        
    return {
        "statusCode": 200,
        "body": {"message": description}
    }
