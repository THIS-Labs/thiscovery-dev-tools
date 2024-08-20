#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2019 THIS Institute
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   A copy of the GNU Affero General Public License is available in the
#   docs folder of this project.  It is also available www.gnu.org/licenses/
#
SUCCESSFUL_LOGIN = {
    "detail-type": "Auth0 log",
    "resources": [],
    "id": "6b4bc671-0217-46ca-8ee0-e663c94abd91",
    "source": "aws.partner/auth0.com/thiscovery-2308531e-1ba0-4824-a5de-5fa1d5928ea4/auth0.logs",
    "time": "2021-01-16T12:12:43Z",
    "detail": {
        "data": {
            "date": "2021-01-16T12:12:30.147Z",
            "log_id": "80020210116121232560015923748216455316604749397232713763",
            "user_name": "altha@email.co.uk",
            "ip": "3a02:c7d:bb78:ad10:343c:4c88:60cb:be04",
            "strategy_type": "database",
            "type": "s",
            "client_id": "WflrpooXWyDv3vzf6LxIzYBd6fafewjw",
            "hostname": "thiscovery.eu.auth0.com",
            "connection_id": "con_C85rtu1sSH9UFXmR",
            "user_id": "auth0|6012d7eccvf1c41076d8ed3d",
            "connection": "Username-Password-Authentication",
            "details": {
                "session_id": "dt1G5nlxkGV10uJx4sKKBH7hwEVbaHAx",
                "initiatedAt": 1610799117840,
                "completedAt": 1610799150146,
                "stats": {"loginsCount": 1},
                "prompts": [
                    {
                        "initiatedAt": 1610799149624,
                        "completedAt": 1610799149961,
                        "connection_id": "con_C85rtu1sSH9UFXmR",
                        "stats": {"loginsCount": 1},
                        "identity": "6012d7eccvf1c41076d8ed3d",
                        "name": "lock-password-authenticate",
                        "connection": "Username-Password-Authentication",
                        "strategy": "auth0",
                        "session_user": "7102e82d05c97d006e666478",
                        "elapsedTime": 337,
                    },
                    {
                        "initiatedAt": 1610799117842,
                        "completedAt": 1610799149964,
                        "timers": {"rules": 153},
                        "user_id": "auth0|6012d7eccvf1c41076d8ed3d",
                        "user_name": "altha@email.co.uk",
                        "name": "login",
                        "flow": "login",
                        "elapsedTime": 32122,
                    },
                ],
                "elapsedTime": 32306,
            },
            "strategy": "auth0",
            "client_name": "Thiscovery",
            "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-A908B Build/QP1A.190711.020; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/87.0.4280.141 Mobile Safari/537.36 EdgW/1.0",
        },
        "log_id": "80020210116121232560015923748216455316604749397232713763",
    },
    "region": "eu-west-1",
    "version": "0",
    "account": "696982352112",
}

SUCCESSFUL_REGISTRATION = {
    "detail-type": "Auth0 log",
    "resources": [],
    "id": "REDACTED",
    "source": "REDACTED",
    "time": "2022-02-25T10:48:43Z",
    "detail": {
        "data": {
            "date": "2022-02-25T10:48:31.036Z",
            "log_id": "90020220225104831160441788900872658485194909784700092514",
            "user_name": "altha@email.co.uk",
            "ip": "REDACTED",
            "description": "",
            "strategy_type": "database",
            "type": "ss",
            "client_id": "REDACTED",
            "connection_id": "con_C72rtu1sAF9UFXmR",
            "user_id": "REDACTED",
            "connection": "Username-Password-Authentication",
            "details": {
                "body": {
                    "password": "*****",
                    "user_metadata": {
                        "last_name": "Alcorn",
                        "country": "GB",
                        "first_name": "Altha",
                        "citsci_uuid": "d1070e81-557e-40eb-a7ba-b951ddb7ebdc",
                    },
                    "name": "Altha Alcorn",
                    "connection": "Username-Password-Authentication",
                    "tenant": "thiscovery",
                    "client_id": "REDACTED",
                    "email": "altha@email.co.uk",
                }
            },
            "strategy": "auth0",
            "client_name": "Thiscovery",
            "user_agent": "GuzzleHttp/6.3.3 curl/7.58.0 PHP/7.4.26",
        },
        "log_id": "90020220225104831160441788900872658485194909784700092514",
    },
    "region": "REDACTED",
    "version": "0",
    "account": "REDACTED",
}

SUCCESSFUL_VERIFICATION = {
    "version": "0",
    "id": "f622ae9e-d48b-e651-db3e-e83ea16e58b8",
    "detail-type": "Auth0 log",
    "source": "aws.partner/auth0.com/thiscovery-18bef42e-b354-431d-986c-d3f0207cb5d5/auth0.logs",
    "account": "REDACTED",
    "time": "2024-08-19T13:10:45Z",
    "region": "REDACTED",
    "resources": [],
    "detail": {
        "log_id": "90020240819131045716103000000000000001223372090513925864",
        "data": {
            "client_id": "REDACTED",
            "client_name": "Thiscovery",
            "connection": "Username-Password-Authentication",
            "connection_id": "REDACTED",
            "date": "2024-08-19T13:10:45.657Z",
            "description": "Your email was verified. You can continue using the application.",
            "details": {
                "email": "clive@email.co.uk",
                "query": {
                    "client_id": "REDACTED",
                    "connection": "Username-Password-Authentication",
                    "email": "clive@email.co.uk",
                    "idp_user_id": None,
                    "includeEmailInRedirect": True,
                    "resultUrl": "REDACTED",
                    "tenant": "thiscovery",
                    "user_id": "auth0|1234abcd",
                },
            },
            "ip": "REDACTED",
            "strategy": "auth0",
            "strategy_type": "database",
            "type": "sv",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "user_id": "auth0|1234abcd",
            "user_name": "clive@email.co.uk",
            "log_id": "90020240819131045716103000000000000001223372090513925864",
            "tenant_name": "thiscovery",
        },
    },
}
