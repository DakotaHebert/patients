import json
from datetime import datetime
from datetime import timedelta

from src.lib.dynamo import appointment_table


def lambda_handler(event, context):
    provider_id = event["provider_id"]
    slot_id = event["slot_id"]

    try:
        slot_time = datetime.fromisoformat(slot_id)
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps("Invalid slot_id format. Expected ISO 8601 format."),
        }

    availability_date = slot_time.strftime("%Y-%m-%d")
    start_time = slot_time.strftime("%H:%M")

    # Fetch current availability
    response = appointment_table.get_item(
        Key={"provider_id": provider_id, "availability_date": availability_date}
    )

    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps("Availability not found")}

    item = response["Item"]
    available_slots = item.get("available_slots", {})

    # Find and remove the specific 15-minute slot
    slot_duration = timedelta(minutes=15)
    slot_end_time = (slot_time + slot_duration).strftime("%H:%M")

    if start_time not in available_slots:
        return {
            "statusCode": 404,
            "body": json.dumps("Time slot not found in availability"),
        }

    current_end_time = available_slots[start_time]

    if slot_end_time >= current_end_time:
        # The requested slot exceeds the current available slot range
        del available_slots[start_time]
    else:
        # Add a new time entry for the slot immediately following the booked slot
        new_start_time = (slot_time + slot_duration).strftime("%H:%M")
        new_end_time = current_end_time
        available_slots[new_start_time] = new_end_time

    # Update the availability in DynamoDB
    appointment_table.update_item(
        Key={"provider_id": provider_id, "availability_date": availability_date},
        UpdateExpression="SET available_slots = :val",
        ExpressionAttributeValues={":val": available_slots},
    )

    return {"statusCode": 200, "body": json.dumps("Time slot updated successfully")}
