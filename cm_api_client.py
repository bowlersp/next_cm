import os
from dotenv import load_dotenv
import requests
import json
from time import sleep

'''
Load environment variables from the .env file

Example .env format:

ENDPOINT=testcmapi.f5demo.com
USERNAME=thebestusername
PASSWORD=theworstpassword
'''
load_dotenv()

endpoint = os.getenv("ENDPOINT")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

'''
Read the contents of a file containing an AS3
declaration, then convert it to a JSON object
'''
def read_declaration(filename):
    with open(filename) as file:
        declaration = file.read()
    declaration = json.loads(declaration)
    return declaration

'''
Each workflow-specific function should leverage the api_call
function so that login / access token obtainment and REST 
method executions are handled consistently.
'''
def api_call(endpoint, method, uri, access_token, data=None):
    if method in ["get", "patch", "put", "post", "delete"]:
        headers = {"Content-Type": "application/json"}

        # If no access token is provided, attempt to obtain
        # one via the login process. Bail out if the login
        # attempt fails. Otherwise, continue on and perform
        # the respective REST method and return the
        # JSON response object
        if access_token != "":
            headers["Authorization"] = f"Bearer {access_token}"
        else:
            r = requests.post(f"https://{endpoint}/api/login", headers=headers, data=json.dumps({"username": username, "password": password}))
            if "access_token" in r.json().keys():
                access_token = r.json()["access_token"]
                headers["Authorization"] = f"Bearer {access_token}"
            else:
                status = r.json()["status"]
                return f"Authoriation failed with a {status} error"

        if method == "get":
            response = requests.get(f"https://{endpoint}{uri}", headers=headers)
        elif method == "patch":
            response = requests.patch(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data))
            print(response.json())
        elif method == "put":
            response = requests.put(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data))
        elif method == "post":
            response = requests.post(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data))
        elif method == "delete":
            response = requests.delete(f"https://{endpoint}{uri}", headers=headers)

        return response.status_code, response.json()
    else:
        return 400, f"Invalid method '{method}'"

'''
Search the application services declarations
for a specific tenant name and return its ID
'''
def get_declaration_by_name(name):
    uri = "/mgmt/shared/appsvcs/declare"
    status_code, r = api_call(endpoint=endpoint, method="get", uri=uri, access_token="", data="")

    if "_embedded" in r:
        appsvcs = r["_embedded"]["appsvcs"]
        for appsvc in appsvcs:
            if appsvc["tenant_name"] == name:
                return True, appsvc["id"]

    return False, f"Unable to find deploymant with tenant name {name}"

'''
POST an AS3 declaration to the CM API
'''
def post_declaration(declaration):
    uri = "/mgmt/shared/appsvcs/declare"
    status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=declaration)
    
    if status_code == 400:
        return False, r
    else:
        return True, r["id"]

'''
PATCH an AS3 declaration in the CM API
'''
def patch_declaration(declaration):
    uri = "/mgmt/shared/appsvcs/declare"
    status_code, r = api_call(endpoint=endpoint, method="patch", uri=uri, access_token="", data=declaration)

    return r["id"]


'''
PUT an AS3 declaration to the CM 
'''
def put_declaration(declaration_id, declaration):    
    uri = f"/mgmt/shared/appsvcs/declare/{declaration_id}"
    status_code, r = api_call(endpoint=endpoint, method="put", uri=uri, access_token="", data=declaration)

    return r["id"]

'''
DELETE an AS3 declaration from the CM API
'''
def delete_declaration(declaration_id):
    uri = f"/mgmt/shared/appsvcs/declare/{declaration_id}"
    status_code, r = api_call(endpoint=endpoint, method="delete", uri=uri, access_token="")

    return r["message"]

'''
Deploy an AS3 declaration to Next instances
from the CM API
'''
def deploy_declaration(declaration_id, instances):
    uri = f"/mgmt/shared/appsvcs/declare/{declaration_id}/deployments"
    instance_count = len(instances)
    success_count = 0
    failed_instances = []
    for instance in instances:
        data = {"target":f"{instance}"}
        status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=data)
        if status_code == 202:
            success_count += 1
        else:
            failed_instances.append(instance)
    
    if success_count == instance_count:
        return True, r
    else:
        return False, f"{success_count} of {instance_count} were successful. The following failed: {', '.join(failed_instances)}"

'''
Run through the following sequence of events:

1. Read AS3 declaration from a local file
2. POST the AS3 declaration to the CM API
3. Deploy the AS3 declaration to a Next instance from
   the CM API
4. Search CM's AS3 declarations for a specific tenant
   and return the ID
5. Delete the deployed declaration via ID
'''
def main():
    # Load v1 of the declaration from a file
    # declaration_v1_filename = "irule_demo_app001_04_v1.json"
    declaration_v1_filename = "irule_demo_app001_04_v1.json"
    print(f"\nReading AS3 declaration from '{declaration_v1_filename}'\n")
    v1_declaration = read_declaration(declaration_v1_filename)

    # The creation and deployment of a declaration
    print("Sending AS3 declaration to CM API")
    as3_v1_created, declaration_id = post_declaration(v1_declaration)
    if as3_v1_created:
        print(f"AS3 Declaration with ID {declaration_id} has been created\n")
    else:
        print(f"AS3 Declaration creation failed with message: {declaration_id}")
        return

    instances = ["10.1.1.11", "10.1.1.100"]
    print(f"Deploying v1 AS3 declaration ID {declaration_id} to {', '.join(instances)}")
    deploy_success, deploy_message = deploy_declaration(declaration_id, instances)
    if deploy_success:
        print(f"AS3 Deployment succeeded with result: {deploy_message}\n")
    else:
        print(f"AS3 Deployment failed with message: {deploy_message}")

    # Execute a brief pause while the declaration is consumed and deployed
    sleep(2)

    # Attempt retrieving a declaration by tenant name
    tenant_name = "testTenant001"
    print(f"Searching AS3 declarations for tenant named '{tenant_name}'")
    search_success, declaration_id = get_declaration_by_name(tenant_name)
    if search_success:
        print(f"Successfully found AS3 tenant {tenant_name} with ID {declaration_id}\n")
    else:
        print(f"AS3 tenant search failed with message: {declaration_id}")
        return

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    input("Press Enter to continue with updating and redeploying the AS3 declaration\n")

    # Load v2 of the declaration from a file
    declaration_v2_filename = "irule_demo_app001_04_v2.json"
    print(f"\nReading AS3 declaration from '{declaration_v2_filename}'\n")
    v2_declaration = read_declaration(declaration_v2_filename)

    # Update the AS3 declaration to v2 which,
    # adds pool members to the app service
    print(f"Updating AS3 declaration ID {declaration_id}")
    declaration_id = put_declaration(declaration_id, v2_declaration)
    print(f"AS3 Declaration with ID {declaration_id} has been updated\n")

    # Execute a brief pause while the declaration is consumed and deployed
    sleep(2)

    # Deploy v2 of the AS3 declaration
    # This is commented out because currently it does not appear
    # this is the proper way to redeploy a declaration, as a response of
    # 'AS3-0008: AS3 Validation Error: Application is already deployed to the BIG-IP Next instance'
    #
    # I have attempted manually updating the AS3 declaration within CM's
    # UI, and still does not show the pool members, even though the
    # AS3 declaration is successfully processed.
    #
    # print(f"Deploying v2 of AS3 declaration ID {declaration_id} to {', '.join(instances)}")
    # deploy_result = deploy_declaration(declaration_id, instances)
    # print(f"Deployment result: {deploy_result}\n")
    #

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    input("Press Enter to continue with deletion of the AS3 declaration\n")

    # Delete the declaration
    print(f"Deleting declaration with ID of {declaration_id}")
    deletion_message = delete_declaration(declaration_id)
    print(f"{declaration_id}: {deletion_message}\n")


main()