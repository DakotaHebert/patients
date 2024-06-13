import boto3

# A dynamo table to track availability
dynamodb = boto3.resource("dynamodb")
table_name = "availibility"
availibility_table = dynamodb.Table(table_name)

"""
Table structure would look something like:
{
  "provider_id": "provider123",  <--- Primary Key
  "availability_date": "2023-07-10", <--- Sort Key
  "available_slots" : {
    "start_time": "end_time",
    "08:00": "17:00".
  }
}
"""

table_name = "appointments"
appointment_table = dynamodb.Table(table_name)

"""
{
    "user_id": uuid, <--- Primary Key
    "appointment_id: uuid, <--- Sort Key
    "date": "2023-07-10", 
    "start_time": "08:00", # End time will be 15 minutes after
    "status": ["PENDING", "DENIED", "EXPIRED", "CONFIRMED"]
}
"""