# Telegram integration

## Introduction

In this document we describe how to configure ADS to send messages via a
Telegram Bot.

First we need to create a Telegram Bot for this purpose. The Telegram
part is out of scope for this tutorial, but for more information see the
official website for Telegram (<https://core.telegram.org/bots>)

When the Bot is created we receive an API-Key. Together with the Chat-ID
and the API-Key we have ingredients to launch a message from ADS to
Telegram.

## ADS configuration

For the configuration in ADS we have to upload the “telegram.sh” script
first. (find the script in the attachment)

We browse to ADS \>\> Settings \>\> SYSTEM SETTINGS \>\> Custom scripts
\>\> + NEW CUSTOM SCRIPT

Give the script a name, upload the file “telegram.sh” fill in the
parameters. In the value field put the only the description. We put the
value later, this makes the script more flexible. Now you can save the
script.

We give the action a meaningful name select the script from the list we
just created.

In the field –API-Key we fill in the API Key we got from the Telegram
Bot and in the –chat\_id we put the belonging Chat-ID

Now we have to select a perspective. In this perspective we defined the
ADS events we like to receive via Telegram.

The last part is set the action active and select the minimum priority
to trigger the message.

Now we can click save.

We find the new scrip now active under “Custom scripts”


Depending on how the perspective is configured, you receive the ADS
event alerts with de corresponding priority.
