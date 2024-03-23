1) authenticate
2) get rSeries provider id
https://{{endpoint}}/api/v1/spaces/default/providers/f5os
{
    "_embedded": {
        "providers": [
            {
                "_links": {
                    "self": {
                        "href": "/api/v1/spaces/default/providers/f5os/88b58b89-c2c1-44f8-879a-a93bea29fddc"
                    }
                },
                "connection": {
                    "authentication": {
                        "type": "basic",
                        "username": "admin"
                    },
                    "host": "192.168.1.252:8888"
                },
                "id": "88b58b89-c2c1-44f8-879a-a93bea29fddc",
                "name": "r5900",
                "type": "RSERIES"
            }
        ]
    },
    "_links": {
        "self": {
            "href": "/v1/providers/f5os"
        }
    }
}
2) send tenant deployment declaration
    https://clouddocs.f5.com/products/big-iq/mgmt-api/v0.0.1/ApiReferences/bigip_public_api_ref/r_openapi-next.html#tag/Instance/operation/RunRseriesInstantiationTask

    POST https://{{endpoint}}/api/device/api/v1/spaces/default/instances/instantiation/rseries
    {
  "provider_id": "88b58b89-c2c1-44f8-879a-a93bea29fddc",
  "next_instances": [
    {
      "hostname": "bowler-rseries-next-01.bigip.com",
      "tenant_image_name": "BIG-IP-Next-20.1.0-2.279.0+0.0.75",
      "tenant_deployment_file": "BIG-IP-Next-20.1.0-2.279.0+0.0.75.yaml",
      "nodes": [
        1
      ],
      "mgmt_ip": "192.168.1.170",
      "mgmt_prefix": 24,
      "mgmt_gateway": "192.168.1.9",
      "cpu_cores": 4,
      "disk_size": 25,
      "timeout": 360,
      "vlans": [
        111,
        112
      ],
      "admin_password": "admin.F5kc.lab"
    }
  ]
}

response
{
    "_links": {
        "self": {
            "href": "/api/v1/spaces/default/instances/instantiation-tasks/89e01e07-e9bd-4200-89f9-425937d78002"
        },
        "vm": {
            "href": "/v1/nodes/unknown"
        }
    },
    "created": "2024-03-23T04:39:54.579417Z",
    "id": "89e01e07-e9bd-4200-89f9-425937d78002",
    "name": "create Instantiation 88b58b89-c2c1-44f8-879a-a93bea29fddc",
    "node_id": null,
    "provider_id": "88b58b89-c2c1-44f8-879a-a93bea29fddc",
    "provider_type": "RSERIES",
    "state": "instantiateInstances",
    "status": "running",
    "task_payload": {
        "provider_id": "88b58b89-c2c1-44f8-879a-a93bea29fddc",
        "next_instances": [
            {
                "nodes": [
                    1
                ],
                "vlans": [
                    111,
                    112
                ],
                "mgmt_ip": "192.168.1.170",
                "timeout": 360,
                "hostname": "bowler-rseries-next-01.bigip.com",
                "cpu_cores": 4,
                "disk_size": 25,
                "mgmt_prefix": 24,
                "mgmt_gateway": "192.168.1.9",
                "admin_password": "*****",
                "tenant_image_name": "BIG-IP-Next-20.1.0-2.279.0+0.0.75",
                "tenant_deployment_file": "BIG-IP-Next-20.1.0-2.279.0+0.0.75.yaml"
            }
        ]
    },
    "task_type": "instantiation",
    "updated": "2024-03-23T04:39:55.099242Z"
}
3) check status
4) onboard instance
POST https://{{endpoint}}/api/v1/spaces/default/instances
{
    "address": "192.168.1.9",
    "port": 5443,
    "device_user": "admin",
    "device_password": "admin.F5kc.lab",
    "management_user": "admin-cm",
    "management_password": "admin.F5kc.lab",
    "management_confirm_password": "admin.F5kc.lab"
}

response
{
    "_links": {
        "self": {
            "href": "/api/v1/spaces/default/instances/discovery-tasks/1ed9a871-5cb1-4438-8da9-2cbeeb3c73bb"
        }
    },
    "path": "/api/v1/spaces/default/instances/discovery-tasks/1ed9a871-5cb1-4438-8da9-2cbeeb3c73bb"
}
5) check discovery task status -- waiting for user input
get https://{{endpoint}}/api/v1/spaces/default/instances/discovery-tasks/faadc136-6f0e-44bd-bb74-59f0751d7bd2

6) accept cert, PATCH
PATCH https://{{endpoint}}/api/v1/spaces/default/instances/discovery-tasks/faadc136-6f0e-44bd-bb74-59f0751d7bd2
{
    "is_user_accepted_untrusted_cert": true
}

7) license instance
Get Token
GET https://{{endpoint}}/api/v1/spaces/default/license/tokens
[
    {
        "entitlement": "{\"compliance\":{\"digitalAssetComplianceStatus\":\"valid\",\"digitalAssetDaysRemainingInState\":0,\"digitalAssetExpiringSoon\":false,\"digitalAssetOutOfComplianceDate\":\"\",\"entitlementCheckStatus\":\"valid\",\"entitlementExpiryStatus\":\"valid\",\"telemetryStatus\":\"valid\",\"usageExceededStatus\":\"valid\"},\"documentType\":\"\",\"documentVersion\":\"\",\"digitalAsset\":{\"digitalAssetId\":\"\",\"digitalAssetName\":\"\",\"digitalAssetVersion\":\"\",\"telemetryId\":\"\"},\"entitlementMetadata\":{\"complianceEnforcements\":[\"entitlement\"],\"complianceStates\":{\"device-twin\":[\"in-grace-period\",\"in-enforcement-period\",\"non-functional\"],\"entitlement\":[\"in-grace-period\",\"in-enforcement-period\",\"non-functional\"],\"telemetry\":[\"in-grace-period\",\"in-enforcement-period\",\"non-functional\"],\"usage\":[\"in-grace-period\",\"in-enforcement-period\"]},\"enforcementBehavior\":\"visibility\",\"enforcementPeriodDays\":0,\"entitlementModel\":\"fixed\",\"expiringSoonNotificationDays\":7,\"entitlementExpiryDate\":\"2024-04-20T20:12:10.345Z\",\"gracePeriodDays\":0,\"nonContactPeriodHours\":0,\"nonFunctionalPeriodDays\":14,\"orderSubType\":\"\",\"orderType\":\"eval\"},\"subscriptionMetadata\":{\"programName\":\"big_ip_next_trial\",\"programTypeDescription\":\"big_ip_next_trial\",\"subscriptionId\":\"TRL-154207\",\"subscriptionExpiryDate\":\"\",\"subscriptionNotifyDays\":\"\"},\"RepositoryCertificateMetadata\":{\"sslCertificate\":\"\",\"privateKey\":\"\"},\"entitledFeatures\":[{\"entitledFeatureId\":\"17c8fea3-5dbf-48b9-a071-88f995fe4504\",\"featureFlag\":\"bigip_active_assets\",\"featurePermitted\":100,\"featureRemain\":75,\"featureUnlimited\":false,\"featureUsed\":25,\"featureValueType\":\"integral\",\"uomCode\":\"\",\"uomTerm\":\"\",\"uomTermStart\":0}]}",
        "orderSubType": "",
        "orderType": "eval",
        "shortName": "next-trial-01",
        "subscriptionExpiry": "2024-04-20T20:12:10Z",
        "tokenId": "2c7f7282-96fb-4c04-b345-aaacd517993a"
    }
]

Get Next Instance ID
GET https://{{endpoint}}/api/v1/spaces/default/instances
1c551661-8bd2-4754-bfef-8dc168aac4f8

Activate Token on Instance
POST https://{{endpoint}}/api/llm/tasks/license/activate
[
    {
        "digitalAssetId": "1c551661-8bd2-4754-bfef-8dc168aac4f8",
        "jwtId": "2c7f7282-96fb-4c04-b345-aaacd517993a"
    }
]

response
{
    "1c551661-8bd2-4754-bfef-8dc168aac4f8": {
        "_links": {
            "self": {
                "href": "/license-task/65986593-0ad2-4d2e-b7f2-28a63e550d81"
            }
        },
        "accepted": true,
        "deviceId": "1c551661-8bd2-4754-bfef-8dc168aac4f8",
        "reason": "",
        "taskId": "65986593-0ad2-4d2e-b7f2-28a63e550d81"
    }
}

8) configure networking
CANNOT FIND A WAY TO DO THIS VIA API DOCUMENTATION

Followed browser network activity to see this
Why is it updating the tenant to use 2vCPU and 22 GB disk space? That's not reflected on the tenant itself, as validated via the rSeries F5OS UI

PATCH https://10.11.0.10/api/device/v1/instances/1c551661-8bd2-4754-bfef-8dc168aac4f8
{"template_name":"default-standalone-rseries","parameters":{"hostname":"","l1Networks":[{"vlans":[{"selfIps":[{"address":"10.11.1.170/24"}],"name":"External-Bowler-111","tag":111},{"selfIps":[{"address":"10.11.2.170/24"}],"name":"Internal1-Bowler-112","tag":112}],"l1Link":{"linkType":"Interface","name":"1.1"},"name":"3.0"}],"default_gateway":"","management_address":"192.168.1.170","rseries_properties":[{"vlan_ids":[],"cpu_cores":2,"disk_size":22,"tenant_image_name":"none","tenant_deployment_file":"none"}],"instantiation_provider":[{"id":"00000000-0000-0000-0000-000000000000","type":"rseries"}],"management_network_width":24,"management_credentials_password":"*****","management_credentials_username":"admin-cm","instance_one_time_password":"XVlB<0_;$<6Z"}}

9) provision modules (if SSLO or Access are needed)
    https://clouddocs.f5.com/products/big-iq/mgmt-api/v0.0.1/ApiReferences/bigip_public_api_ref/r_openapi-next.html#tag/Instance/operation/RunModuleProvisionTask

10) Create FAST App Service
Retain FAST app service ID to be used in step 11

POST https://{{endpoint}}/mgmt/shared/fast/appsvcs/
{
    "name": "juice-shop-app",
    "template_name": "http",
    "set_name": "Examples",
    "parameters": {
        "pools": [
            {
                "servicePort": 3000,
                "loadBalancingMode": "round-robin",
                "monitorType": [
                    "http"
                ],
                "poolName": "juice-shop-pool"
            }
        ],
        "virtuals": [
            {
                "iRulesEnum": [],
                "ciphers": "DEFAULT",
                "enable_Access": false,
                "tls_c_1_2": true,
                "tls_c_1_3": false,
                "enable_TLS_Server": false,
                "ciphers_server": "DEFAULT",
                "tls_s_1_2": true,
                "tls_s_1_3": false,
                "enable_snat": true,
                "snat_automap": true,
                "snat_addresses": [],
                "enable_FastL4": false,
                "FastL4_idleTimeout": 600,
                "FastL4_looseClose": true,
                "FastL4_looseInitialization": true,
                "FastL4_resetOnTimeout": true,
                "FastL4_tcpCloseTimeout": 43200,
                "FastL4_tcpHandshakeTimeout": 43200,
                "enable_HTTP2_Profile": false,
                "enable_UDP_Profile": false,
                "UDP_idle_timeout": 60,
                "enable_TCP_Profile": false,
                "TCP_idle_timeout": 60,
                "enable_mirroring": true,
                "enable_TLS_Client": false,
                "enable_WAF": false,
                "enable_iRules": false,
                "virtualPort": 80,
                "virtualName": "juice-shop-vs",
                "pool": "juice-shop-pool"
            }
        ],
        "application_description": "",
        "application_name": "juice-shop-app"
    },
    "allowOverwrite": true
}

response
{
    "_links": {
        "self": {
            "href": "/appsvcs"
        }
    },
    "id": "0ee89eb2-3a94-4a09-ac8b-fd63b787c34c",
    "message": "application created successfully",
    "status": 200
}

11) Deploy FAST App Service
POST https://{{endpoint}}/mgmt/shared/fast/appsvcs/{{fast_appsvc_id}}/deployments
{
    "deployments": [
        {
            "parameters": {
                "pools": [
                    {
                        "poolName": "juice-shop-pool",
                        "poolMembers": [
                            {
                                "name": "bowler-ubuntu-juice-shop",
                                "address": "10.11.2.200"
                            }
                        ]
                    }
                ],
                "virtuals": [
                    {
                        "virtualName": "juice-shop-vs",
                        "virtualAddress": "10.11.1.200"
                    }
                ]
            },
            "target": {
                "address": "192.168.1.170"
            },
            "allow_overwrite": true
        }
    ]
}

response
{
    "_links": {
        "self": {
            "href": "/appsvcs/0ee89eb2-3a94-4a09-ac8b-fd63b787c34c/deployments"
        }
    },
    "deployments": [
        {
            "deploymentID": "aba0b94d-794d-4cc5-a36e-deafd678a86e",
            "instanceID": "1c551661-8bd2-4754-bfef-8dc168aac4f8",
            "status": "pending",
            "taskID": "aa96ec16-c12a-47ee-9312-59495d4d9fe8",
            "task_type": "CREATE"
        }
    ],
    "id": "0ee89eb2-3a94-4a09-ac8b-fd63b787c34c"
}

Creating a template assumes you know exactly what you're doing. There's no help or guidance on what the Template Body should contain.

Next step: go look at the 'http' template body and see how easy it is to interpret

