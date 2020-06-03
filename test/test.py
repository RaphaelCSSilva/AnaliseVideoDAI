from datetime import datetime, timedelta
from pytz import timezone
import pytz

pt_timezone = timezone('Europe/London')
print(pt_timezone.zone)

print(datetime.now(pt_timezone).strftime("%Y-%m-%dT%H_%M_%S%z"))
print(datetime.now().strftime("%Y-%m-%dT%H_%M_%S%z"))

print(datetime.now(pt_timezone).strftime("%Y-%m-%dT%H_%M_%S+01:00 Europe/London"))
print(datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H_%M_%S%z"))

print(datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S%z+01:00"))