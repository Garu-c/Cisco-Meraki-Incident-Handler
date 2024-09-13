# Automation Project of Cisco Meraki Incident: Uplink Status Changed

## Introduction

In my previous job, there was an incident handled by the monitoring area (NOC - First Support) that was a bit annoying and repetitive. They received the incident ticket (Uplink Status Changed) and basically closed it after a quick look at the Meraki Dashboard website; rarely did they actually work on a troubleshooting case where the Internet link was down, so 90% of the time it was a "false positive."

So they brought the case to me, asking if there was a way to check if the link was really down and, if so, move the incident ticket to the queue where they work in Autotask. In the case of a "false positive" (the link is up), I would just close the ticket, providing evidence in the ticket description.

Here's the solution I came up with. It was my first Python script in the company, so don't judge me too harshly — I was, and still am, learning to code XD


## AutoTaskApi.py - The MakeAutoTaskApiCall Class

The 'MakeAutoTaskApiCall' class is designed to automate ticket management and create basic functions to manage ticket entities using the AutoTask API. Its primary functionalities include:

- **Ticket Query**: Retrieves a list of open tickets based on filters such as client name and incident type.
- **Lock File Check**: Ensures that the same ticket is not processed multiple times by checking for existing lock files. It redirects tickets to an automation queue if no lock file is present.
- **Ticket Closure**: Automatically closes tickets based on the device status. If a problem persists (device status down), it moves the ticket to a monitoring (NOC) queue; if resolved (status up), it closes the ticket.
- **Ticket Management**: Maintains lock file records of ticket status and updates ticket information in the AutoTask API.
This class helps streamline the handling of support tickets by automating the querying, updating, and closing processes, thereby improving efficiency in incident management.


## uplink.py (The main script)

This is the script that you actually run. It interacts with the Meraki SDK API and the previous AutoTask class to validate the status of the devices in the Meraki Dashboard website. The main functionalities include:

- **Meraki API Dashboard Integration**: Returns organization, network, and device information, monitoring their statuses.
- **Device Validation Based on Network Name/Device Name**: Checks the device statuses based on ticket information.
- **Incident Ticket Automation**: If the device statuses are down, the script attempts to revalidate the statuses over time with customizable retry intervals. If the problem still persists, it redirects the ticket to the monitoring queue.
- **Error Handling**: Handles possible Meraki API errors, such as expired licenses and other authentication issues.