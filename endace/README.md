# Flowmon ADS Integration with Endace

## Python Script — ADS REST API (Recommended)

The `add-comment-api.py` script adds a comment to each ADS event it processes. The comment contains an Endace **Pivot-to-Vision** link. The link opens EndaceVision with the event time, the event title and the source IP address already filled in, so the analyst can go straight from the ADS event to the recorded packets.

The script adds the comment through the Flowmon ADS REST API endpoint `/rest/ads/v1/event/add-comment`. It doesn't write to the ADS database directly.

> **Note:** This script works only with **Flowmon ADS 13.1** and newer. The `add-comment` REST API endpoint is not available in older versions. For older versions, use the legacy `add-comment.py` script described below.

### Endace Configuration

You need the hostname or IP address of the EndaceProbe and the data sources to query (for example `target:all`). Users who open the link must be able to log in to the EndaceProbe web UI.

### Flowmon ADS Configuration

This script has been tested with Flowmon ADS 13.1.

Details on configuring a custom script action are in the [User Guide](https://docs.progress.com/bundle/progress-flowmon-ads-13-1/page/topics/user-guide/Event-Response.html#custom-scripts) of Flowmon ADS.

The script logs in to the Flowmon REST API, so it needs a user account that is allowed to comment ADS events. By default it connects to `localhost`, which is the appliance where ADS runs the script.

You have two options for providing the configuration:

**Option 1 — Embed directly in the script** before uploading it to ADS. Edit the configuration section at the top of the script:

```python
# IP / hostname of Endace probe
PROBE = 'pp9-1.lab.endace.com'
# Data sources for the Endace query
SOURCES = 'target:all'
# Flowmon appliance REST API connection (user needs permission to comment ADS events)
FLOWMON_HOST = 'localhost'
FLOWMON_USER = 'admin'
FLOWMON_PASS = 'admin'
# Verify HTTPS certificate of the Flowmon appliance: True, False or path to a CA bundle.
# Keep certificate verification enabled whenever FLOWMON_HOST is not localhost.
VERIFY_SSL = False
# Log file (directory is writable by ADS scripts)
LOG_FILE = '/data/components/apps/log/endace-add-comment.log'
# Timeout in seconds for REST API requests
TIMEOUT = 30
```

> **Note:** Use a dedicated Flowmon user that has only the permissions needed to comment ADS events. Don't use the `admin` account.

> **Note:** Certificate verification is disabled by default because the script connects to `localhost`. If you set `FLOWMON_HOST` to a remote appliance, set `VERIFY_SSL` to `True` or to the path of a CA bundle that signed the appliance certificate. Otherwise the credentials can be intercepted.

**Option 2 — Pass as parameters** when you configure the custom script action in the ADS UI. Parameters override the values embedded in the script.

> **Note:** Embed the password in the script instead of using `--pass`. Values passed as parameters are visible in the ADS UI, and other processes on the appliance can read them from the process command line while the script runs.

```
usage: add-comment-api.py <options>

Optional:
    --probe <host>     IP / hostname of Endace probe
    --sources <src>    Data sources for the query
    --host <host>      Flowmon appliance with ADS (default localhost)
    --user <username>  Username used for the authentication to Flowmon appliance
    --pass <password>  Password for the user authentication
```

The script writes its log to `/data/components/apps/log/endace-add-comment.log`, which rotates at 5 MB and keeps 4 old files. Check this file if comments don't appear on events.

### Testing

You can test the script from the command line of the Flowmon appliance. Send a tab-separated event line to it in the format that ADS uses. The fields used are the event ID (1st), the timestamp (3rd) and the source IP address (11th):

```bash
printf "2418773\tx\t2026-10-09 10:00:00\tx\tx\tx\tx\tx\tx\tx\t10.0.0.1\n" | python3 add-comment-api.py
```

Then open the event in ADS and check that the comment with the Endace link is there.

---

## Legacy Script — Direct Database Access

> **Note:** The `add-comment.py` script writes comments directly into the ADS database and is installed with the `endace-ptov` package. Use the REST API script above for Flowmon ADS 13.1 and newer.

Details are in the *Endace Kemp Flowmon Deployment Guide* PDF in this folder.
