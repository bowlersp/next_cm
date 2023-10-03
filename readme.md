# AS3 Overview
Use this script as a starting point for interacting with F5 BIG-IP Next Central Manager's (CM) AS3 feature API. The `as3_test()` function executes a basic workflow consisting of the following:

1. **Read** AS3 declaration from a local file
2. **Create** the AS3 declaration via the CM API (POST)
3. **Deploy** the AS3 declaration to an F5 BIG-IP Next instance from
   the CM API (POST)
4. **Search** CM's AS3 declaration API for a specific tenant
   and return the ID (GET)
5. **Delete** the deployed declaration via ID (DELETE)

**PATCH** and **PUT** methods are also plumbed into the script (as seen within the `api_call()` function), but the initial iteration of the test workflow does not leverage them. They will be added to showcase reading and deploying a newer version of an AS3 declaration from a file.

#### UPDATE:
**PATCH** and **PUT** methods for `/mgmt/shared/appsvcs/declare` have been tested, but are not yielding success. Attempts to perform PATCHes against the API result in a 400 Method not allowed error message

```
{
    "message": "method not allowed"
}
```

Attempts to PUT a modified declaration to the CM API appear successful at first, and results are reflected when viewing the declaration with CM's UI, but changes are not observed. The test scenario for this repo involves two versions of a declaration:

1. AS3 decrlation with no pool members
2. AS3 declaration updated to include two pool members

The pool members do not appear under the App Service topology view in the CM UI.


In its current state, the script, when run, will execute a static series of events, due to the fact its designed simply to execute the `main()` function and its contents. The script could, and should, be improved to accept command-line arguments which can be passed in, such as `filename` and `instances`. This would make the script more useable and dynamic rather than fixed and static.

## Prerequisites
Create a local file in the same directory as the project named `.env` and populate it with the following variables:

- `ENDPOINT`
- `USERNAME`
- `PASSWORD`

The file contents should resemble the following:

```
ENDPOINT=testcmapi.f5demo.com
USERNAME=thebestusername
PASSWORD=theworstpassword
```

## Script Execution
Run the following command to initiate the CM API test sequence. The script will pause itself after deploying and self-validating the declaration exists, allowing for manual testing and validation prior to deletion.

```
python3 bigip_next_cm_api_client.py
```


# FAST Application Service (AppSvc) Overview
Use this information as a starting point for interacting with F5 BIG-IP Next CM's FAST Application Service API. The source of JSON files and process was obtained by utilizing Chrome's network developer tools and tracing the API calls. The high-level scenario steps are as follows:

1. Start standard FAST Application Service creation process via CM UI (POST)
2. Define a pool name and service port (PATCH)
3. Define a virtual server name and reference pool (PATCH)
4. Add an iRule to the virtual server / application service (PATCH)
5. Perform Review and Deploy (PATCH)
6. Validate application service (POST [query `?dry_run=true]`)
7. Deploy application service (POST)

There are two distinct parts of this process:

1. Constructing the FAST app service (Steps 1-5)
2. Deploying the FAST app service (Steps 6-7)

These correlate to the following API resources, respectively:

1. mgmt/shared/fast/appsvcs
2. mgmt/shared/fast/appsvcs/{id}/deployments 

When inspecting the JSON files included within `fast_appsvcs`, you'll notice a disction between the FAST app service template and the deployment; pool member and virtual server information are provided separate from the template. Additionally, the target F5 BIG-IP Next instances are defined within the deployment.

`fast_appsvcs/single_step_appsvc_post.json` is a consolidation of steps 1-4 and allows that portion of the process to take place in a single POST, rather than an initial POST for creation followed by PATCHes to update the "draft" app service.

`fast_appsvcs/single_step_appsvc_deployment.json` contains the deployment declaration for the FAST app service created from `fast_appsvcs/single_step_appsvc_post.json`.

The `fast_appsvc_test()` function executes a basic workflow consisting of the following:

1. **Read** FAST Application Service template and deployment declarations from local files
2. **Create** the FAST Application Service via the CM API (POST)
3. **Deploy** the FAST Application Service to an F5 BIG-IP Next instance from
   the CM API (POST)
4. **Search** CM's AS3 declaration API for a specific tenant
   and return the ID (GET)
5. **Delete** the deployed declaration via ID (DELETE)
