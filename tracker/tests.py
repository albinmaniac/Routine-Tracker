from django.test import TestCase

#=======REMINDER EXPLAINATION===========

# Task

# 1. Habit Reminders
# 2. Pending Habit Alerts
# 3. Reset Habit Reminders

# Time (24-hour format)

# 1. 08:00
# 2. 20:00
# 3. 00:00


# Time (12-hour format)

# 1. 8:00 AM
# 2. 8:00 PM
# 3. 12:00 Midnight

# Description

# 1. Sends habit reminders to users every morning at 8 AM.
# 2. Sends alerts for pending habits (not completed) at 8 PM.
# 3. Resets the reminder_sent flag daily at midnight so users can receive reminders the next day.
