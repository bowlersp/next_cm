'''
F5 BIG-IP Next Central Manager API Client Test Script

This simple API client seeks to demonstrate the following features:

 - AS3 declaration creation, deployment, and deletion
 - FAST application service creation, deployment, and deletion

The main() function contains code which triggers AS3 and FAST tests.
The tests currently supported are:

 - as3_test()
 - fast_appsvc_test()

More detailed information about test functions may be found in front of
their respective code blocks.

This flat script is meant to serve as an introduction to managing 
F5 BIG-IP Next application service deployments via the Central Manager API.
Ideally, this should be converted into a class / library so that its
functionality may be referenced within other Python scripts, easing integration
with pre-existing Python-oriented automation processes.
'''

import os
from dotenv import load_dotenv
import requests
import json
from time import sleep

# Silence HTTPS verification warning messages
requests.packages.urllib3.disable_warnings()

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
            r = requests.post(f"https://{endpoint}/api/login", headers=headers, data=json.dumps({"username": username, "password": password}), verify=False)
            if "access_token" in r.json().keys():
                access_token = r.json()["access_token"]
                headers["Authorization"] = f"Bearer {access_token}"
            else:
                status = r.json()["status"]
                return f"Authoriation failed with a {status} error"

        if method == "get":
            response = requests.get(f"https://{endpoint}{uri}", headers=headers, verify=False)
        elif method == "patch":
            response = requests.patch(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data), verify=False)
            print(response.json())
        elif method == "put":
            response = requests.put(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data), verify=False)
        elif method == "post":
            response = requests.post(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data), verify=False)
        elif method == "delete":
            response = requests.delete(f"https://{endpoint}{uri}", headers=headers, verify=False)

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
    print(f"r ::: {r}")
    
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
AS3 Declaration Creation and Deployment Test Process
Run through the following sequence of events:

1. Read AS3 declaration from a local file
2. POST the AS3 declaration to the CM API
3. Deploy the AS3 declaration to a Next instance via
   the CM API
4. Search CM's AS3 declarations for a specific tenant
   and return the ID
5. Delete the deployed declaration via ID
'''
def as3_test():
    # Load v1 of the declaration from a file
    declaration_v1_filename = "as3_declarations/irule_demo_app001_04_v1.json"
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
    declaration_v2_filename = "as3_declarations/irule_demo_app001_04_v2.json"
    print(f"\nReading AS3 declaration from '{declaration_v2_filename}'\n")
    v2_declaration = read_declaration(declaration_v2_filename)

    # Update the AS3 declaration to v2 which,
    # adds pool members to the app service
    print(f"Updating AS3 declaration ID {declaration_id}")
    declaration_id = put_declaration(declaration_id, v2_declaration)
    print(f"AS3 Declaration with ID {declaration_id} has been updated\n")

    # Execute a brief pause while the declaration is consumed and deployed
    sleep(2)
    
    '''
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
    '''

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    input(f"Press Enter to continue with deletion of AS3 declaration ID {declaration_id}\n")

    # Delete the declaration
    print(f"Deleting declaration with ID of {declaration_id}")
    deletion_message = delete_declaration(declaration_id)
    print(f"{declaration_id}: {deletion_message}\n")


'''
Search the FAST Application Services for a 
specific name and return its ID
'''
def get_fast_appsvc_by_name(name):
    uri = "/mgmt/shared/fast/appsvcs/"
    status_code, r = api_call(endpoint=endpoint, method="get", uri=uri, access_token="", data="")

    if "_embedded" in r:
        appsvcs = r["_embedded"]["appsvcs"]
        for appsvc in appsvcs:
            if appsvc["tenant_name"] == name:
                return True, appsvc["id"]

    return False, f"Unable to find FAST Application Service with tenant name {name}"

'''
POST a FAST Application Service Template declaration to the CM API
'''
def post_fast_appsvc(declaration):
    uri = "/mgmt/shared/fast/appsvcs/"
    status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=declaration)
    print(f"post_fast_appsvc ::: {r}")
    
    if status_code == 400:
        return False, r
    elif status_code == 500:
        return False, r["message"]
    else:
        return True, r["id"]

'''
PATCH a FAST Application Service Template declaration in the CM API
'''
def patch_fast_appsvc(fast_appsvc_id, declaration):
    uri = f"/mgmt/shared/fast/appsvcs/{fast_appsvc_id}"
    status_code, r = api_call(endpoint=endpoint, method="patch", uri=uri, access_token="", data=declaration)

    return r["id"]

'''
DELETE a FAST Application Service Template declaration from the CM API
'''
def delete_fast_appsvc(fast_appsvc_id):
    uri =f"/mgmt/shared/fast/appsvcs/{fast_appsvc_id}"
    # uri = f"/mgmt/shared/appsvcs/declare/{fast_appsvc_id}"
    status_code, r = api_call(endpoint=endpoint, method="delete", uri=uri, access_token="")

    return r["message"]

'''
Deploy a FAST Application Service to BIG-IP Next instances
from the CM API
'''
def deploy_fast_appsvc(fast_appsvc_id, deployment):
    uri = f"/mgmt/shared/fast/appsvcs/{fast_appsvc_id}/deployments"
    status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=deployment)
    print(f"deploy_fast_appsvc ::: {r}")

    if status_code == 202:
        return True, r
    else:
        return False, r

'''
FAST Application Service Creation and Deployment Test Process

Run through the following sequence of events:

1. Read a FAST Application Service (appsvc) template from a local file
2. POST the FAST appsvc template to the CM API
3. Deploy the FAST appsvc template to a Next instance via
   the CM API
4. Search CM's FAST appsvc API for a specific name
   and return the ID
5. Delete the deployed FAST appsvc via ID
'''
def fast_appsvc_test():
    # Load the FAST Application Service template declaration from a file
    fast_appsvc_filename = "fast_appsvcs/single_step_appsvc_post.json"
    print(f"\nReading AS3 declaration from '{fast_appsvc_filename}'\n")
    fast_appsvc_template = read_declaration(fast_appsvc_filename)

    # Load the FAST Application Service deployment declaration from a file
    fast_appsvc_deployment_filename = "fast_appsvcs/single_step_appsvc_deployment.json"
    print(f"\nReading AS3 declaration from '{fast_appsvc_deployment_filename}'\n")
    fast_appsvc_deployment = read_declaration(fast_appsvc_deployment_filename)

    # The creation of a FAST Application Service
    print("Sending FAST Application Service template declaration to CM API")
    fast_appsvc_created, fast_appsvc_id = post_fast_appsvc(fast_appsvc_template)
    if fast_appsvc_created:
        print(f"FAST Application Service with ID {fast_appsvc_id} has been created\n")
    else:
        print(f"FAST Application Service creation failed with message: {fast_appsvc_id}")
        return
    
    print(f"Deploying FAST Application Service ID {fast_appsvc_id}")
    fast_appsvc_deploy_success, fast_appsvc_deply_message = deploy_fast_appsvc(fast_appsvc_id, fast_appsvc_deployment)
    if fast_appsvc_deploy_success:
        print(f"FAST Application Deployment succeeded with result: {fast_appsvc_deply_message}\n")
    else:
        print(f"FAST Application Deployment failed with message: {fast_appsvc_deply_message}")

    # Execute a brief pause while the template declaration is consumed and deployed
    sleep(2)

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    input(f"Press Enter to continue with deletion of FAST Application Service ID {fast_appsvc_id}\n")

    # Delete the FAST Application Service and Deployments
    print(f"Deleting FAST Application Service with ID of {fast_appsvc_id}")
    fast_appsvc_deletion_message = delete_fast_appsvc(fast_appsvc_id)
    print(f"{fast_appsvc_id}: {fast_appsvc_deletion_message}\n")

def main():
    # Uncomment the as3_test() line to run the AS3 Declaration API test
    # as3_test()

    # Uncomment the fast_appsvc_test() line to run the FAST Application Service API test
    fast_appsvc_test()

    print("Script end")
    exit()

main()