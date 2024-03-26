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
f5os_endpoint = os.getenv("F5OS_ENDPOINT")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

'''
Set the allowed HTTP methods
'''
ALLOWED_METHODS = ["get", "patch", "put", "post", "delete"]

'''
Set the allowed Providers
'''
ALLOWED_PROVIDERS = ["rseries", "velos", "vsphere"]

'''
ANSI Terminal Formatting
'''
class color:
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

'''
Prettify JSON output
'''
def json_pp(data):
    return json.dumps(data, indent=2)
    

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
    if method in ALLOWED_METHODS:
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
            if data != None:
                response = requests.delete(f"https://{endpoint}{uri}", headers=headers, data=json.dumps(data), verify=False)
            else:
                response = requests.delete(f"https://{endpoint}{uri}", headers=headers, verify=False)

        return response.status_code, response.json()
    else:
        return 400, f"Invalid method '{method}'"

'''
Search for an F5OS Provider by Name
'''
def get_f5os_provider_by_name(name):
    uri = "/api/v1/spaces/default/providers/f5os"
    status_code, r = api_call(endpoint=endpoint, method="get", uri=uri, access_token="", data="")

    if "_embedded" in r:
        providers = r["_embedded"]["providers"]
        for provider in providers:
            if provider["name"] == name:
                return True, provider["id"]
            
    return False, f"Unable to find F5OS provider with name '{name}'"

'''
POST a BIG-IP Next Instance Instantiation Task

'''

def post_instance_instatiation(provider, declaration):
    if provider in ALLOWED_PROVIDERS:
        uri = f"/api/v1/spaces/default/instances/instantiation/{provider}"
        status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=declaration)
        print(f"r ::: {r}")
        
        if status_code == 400:
            return False, r
        else:
            return True, r["path"]
        pass
    else:
        return False, f"Invalid provider '{provider}'. Must be one of {ALLOWED_PROVIDERS}"
    
'''
GET a BIG-IP Next Instance by Name
'''
def get_instance_by_name(name):
    uri = "/api/v1/spaces/default/instances"
    status_code, r = api_call(endpoint=endpoint, method="get", uri=uri, access_token="", data="")

    if "_embedded" in r:
        instances = r["_embedded"]["devices"]
        for instance in instances:
            if instance["hostname"] == name:
                return True, instance["id"]
            
    return False, f"Unable to find BIG-IP Next instance with name '{name}'"
    pass


'''
DELETE a Next Instance

Deleting an instance through this method does NOT delete
the instance from its parent provider.

Also, the rSeries API documentation is.... something to behold.

DELETE https://{{rseries_appliance1_ip}}:8888/restconf/data/f5-tenants:tenants/tenant={{New_Tenant1_Name}}


example response
{'_links': {'self': {'href': '/api/v1/spaces/default/instances/deletion-tasks/4592c271-10f3-4bbe-b9a1-30f5be31543b'}}, 'path': '/api/v1/spaces/default/instances/deletion-tasks/4592c271-10f3-4bbe-b9a1-30f5be31543b'}
'''
def delete_instance(instance_id, tenant_name, f5os_endpoint):
    uri = f"/api/v1/spaces/default/instances/{instance_id}"
    status_code, r = api_call(endpoint=endpoint, method="delete", uri=uri, access_token="",
                              data={"save_backup":True})
    print(status_code, r)

    uri = f"/restconf/data/f5-tenants:tenants/tenant={tenant_name}"
    delete_tenant = requests.delete(f"{f5os_endpoint}{uri}", auth=("kclab", "F5OSisreallycool1!"), verify=False)
    print(delete_tenant.status_code)

    return delete_tenant.status_code

def f5os_provider_instance_test():
    provider_name = "r5900"
    provider_found, provider_id = get_f5os_provider_by_name(provider_name)
    print(provider_found, provider_id)


    rseries_instance_filename = "f5os_provider/rseries_instance.json"
    rseries_instance = read_declaration(rseries_instance_filename)
    rseries_instance_instantiated, rseries_instance_id = post_instance_instatiation("rseries", rseries_instance)
    print(rseries_instance_instantiated, rseries_instance_id)

    input("Press Enter to discover the tenant instance ID.\nYou may need to wait up to 15min.")

    instance_name = "bowler-rseries-next-01"
    instance_found, instance_id = get_instance_by_name(instance_name)
    print(instance_found, instance_id)

    input("Press Enter to continue with instance/tenant deletion")

    deletion_status_code = delete_instance(instance_id, instance_name, f"https://{f5os_endpoint}")
    print(deletion_status_code)

    pass


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
    # uri = "/mgmt/shared/appsvcs/api/v1/spaces/default/appsvcs/documents"
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
    successful_instances = []
    for instance in instances:
        data = {"target":f"{instance}"}
        status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=data)
        if status_code == 202:
            success_count += 1
            successful_instances.append(r)
        else:
            failed_instances.append(instance)
    
    if success_count == instance_count:
        return True, successful_instances
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
    declaration_v1_filename = "as3_declarations/juice-shop_cm-ui.json"
    declaration_v1_filename = "as3_declarations/juice-shop_cm_api_doc.json"
    declaration_v1_filename = "as3_declarations/basic-juice-shop-cm-ui.json"
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

    instances = ["10.1.1.7"]
    print(f"Deploying v1 AS3 declaration ID {declaration_id} to {', '.join(instances)}")
    deploy_success, deploy_message = deploy_declaration(declaration_id, instances)
    if deploy_success:
        print(f"AS3 Deployment succeeded with result:\n{deploy_message}\n")
    else:
        print(f"AS3 Deployment failed with message: {deploy_message}")

    # Execute a brief pause while the declaration is consumed and deployed
    sleep(2)

    # Attempt retrieving a declaration by tenant name
    tenant_name = "JuiceShopTenant"
    print(f"Searching AS3 declarations for tenant named '{tenant_name}'")
    search_success, declaration_id = get_declaration_by_name(tenant_name)
    if search_success:
        print(f"Successfully found AS3 tenant {tenant_name} with ID {declaration_id}\n")
    else:
        print(f"AS3 tenant search failed with message: {declaration_id}")
        return

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    # input("Press Enter to continue with updating and redeploying the AS3 declaration\n")

    # Load v2 of the declaration from a file
    # declaration_v2_filename = "as3_declarations/irule_demo_app001_04_v2.json"
    # print(f"\nReading AS3 declaration from '{declaration_v2_filename}'\n")
    # v2_declaration = read_declaration(declaration_v2_filename)

    # Update the AS3 declaration to v2 which,
    # adds pool members to the app service
    # print(f"Updating AS3 declaration ID {declaration_id}")
    # declaration_id = put_declaration(declaration_id, v2_declaration)
    # print(f"AS3 Declaration with ID {declaration_id} has been updated\n")

    # Execute a brief pause while the declaration is consumed and deployed
    # sleep(2)
    
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
    print(f"{color.BOLD}{color.CYAN}post_fast_appsvc Response:{color.END}\n{json_pp(r)}\n")
    
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
    print(f"{color.BOLD}{color.CYAN}delete_fast_appsvc Response:{color.END}\n{json_pp(r)}\n")
    return r#["message"]

'''
Deploy a FAST Application Service to BIG-IP Next instances
from the CM API
'''
def deploy_fast_appsvc(fast_appsvc_id, deployment):
    uri = f"/mgmt/shared/fast/appsvcs/{fast_appsvc_id}/deployments"
    status_code, r = api_call(endpoint=endpoint, method="post", uri=uri, access_token="", data=deployment)
    print(f"{color.BOLD}{color.CYAN}deploy_fast_appsvc Response:{color.END}\n{json_pp(r)}\n")

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
    print(f"\n{color.BOLD}Reading AS3 declaration from{color.END} '{fast_appsvc_filename}'\n")
    fast_appsvc_template = read_declaration(fast_appsvc_filename)

    # Load the FAST Application Service deployment declaration from a file
    fast_appsvc_deployment_filename = "fast_appsvcs/single_step_appsvc_deployment.json"
    print(f"\n{color.BOLD}Reading AS3 declaration from{color.END} '{fast_appsvc_deployment_filename}'\n")
    fast_appsvc_deployment = read_declaration(fast_appsvc_deployment_filename)

    # The creation of a FAST Application Service
    print(f"{color.UNDERLINE}Sending FAST Application Service template declaration to CM API{color.END}")
    fast_appsvc_created, fast_appsvc_id = post_fast_appsvc(fast_appsvc_template)
    if fast_appsvc_created:
        print(f"{color.BOLD}FAST Application Service with ID{color.END} {fast_appsvc_id} {color.BOLD}has been created{color.END}\n")
    else:
        print(f"FAST Application Service creation failed with message: {fast_appsvc_id}")
        return
    
    input(f"Press {color.BOLD}Enter{color.END} to deploy FAST Application Service ID {fast_appsvc_id}\n")

    
    print(f"{color.UNDERLINE}Deploying FAST Application Service ID{color.END} {fast_appsvc_id}")
    fast_appsvc_deploy_success, fast_appsvc_deply_message = deploy_fast_appsvc(fast_appsvc_id, fast_appsvc_deployment)
    # if fast_appsvc_deploy_success:
    #     print(f"{color.UNDERLINE}FAST Application Deployment succeeded with result:{color.END}\n{json_pp(fast_appsvc_deply_message)}\n")
    # else:
    #     print(f"FAST Application Deployment failed with message: {fast_appsvc_deply_message}")

    # Execute a brief pause while the template declaration is consumed and deployed
    sleep(2)

    # Pause the flow to allow validation within CM UI
    # or testing of the deployed declaration
    input(f"Press {color.BOLD}Enter{color.END} to continue with deletion of FAST Application Service ID {fast_appsvc_id}\n")

    # Delete the FAST Application Service and Deployments
    print(f"{color.UNDERLINE}Deleting FAST Application Service with ID of{color.END} {fast_appsvc_id}")
    fast_appsvc_deletion_message = delete_fast_appsvc(fast_appsvc_id)
    # print(f"{color.UNDERLINE}FAST Deployment Deletion Response:{color.END}\n{json_pp(fast_appsvc_deletion_message)}\n")

def main():
    # Uncomment the f5os_provider_instance_test line to run the F5OS Provider tests
    f5os_provider_instance_test()

    # Uncomment the as3_test() line to run the AS3 Declaration API test
    # as3_test()

    # Uncomment the fast_appsvc_test() line to run the FAST Application Service API test
    # fast_appsvc_test()

    exit()

main()