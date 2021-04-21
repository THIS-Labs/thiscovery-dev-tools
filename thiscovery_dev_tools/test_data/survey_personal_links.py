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
TEST_CREATE_PERSONAL_LINKS_EB_EVENT = {
    "account": "REDACTED",
    "detail": {"account": "cambridge", "survey_id": "SV_2avH1JdVZa8eEAd"},
    "detail-type": "create_personal_links",
    "id": "e0c8d51e-0954-57e8-fdd0-43edaf5bad67",
    "region": "REDACTED",
    "resources": [],
    "source": "thiscovery",
    "time": "2021-03-25T22:46:55Z",
    "version": "0",
}


TEST_UNASSIGNED_PERSONAL_LINK_DDB_ITEM = {
    "account_survey_id": "cambridge_SV_2avH1JdVZa8eEAd",
    "created": "2021-03-25 11:48:31.307081+00:00",
    "details": {
        "contactId": "MLRP_3VsiJYNFbPi6Uyq",
        "email": "no.email@thisinstitute.cam.ac.uk",
        "exceededContactFrequency": False,
        "externalDataReference": None,
        "firstName": None,
        "lastName": None,
        "status": "Email not sent",
        "unsubscribed": "0",
    },
    "expires": "2021-06-23T17:48:30Z",
    "modified": "2021-03-25 11:48:33.007893+00:00",
    "status": "new",
    "type": "personal survey link",
    "url": "https://cambridge.eu.qualtrics.com/jfe/form/SV_2avH1JdVZa8eEAd?Q_DL=EMD_3Tr2Hy8MweBJerm_2avH1JdVZa8eEAd_MLRP_3VsiJYNFbPi6Uyq&Q_CHL=gl",
}


TEST_ASSIGNED_PERSONAL_LINK_DDB_ITEM = {
    **TEST_UNASSIGNED_PERSONAL_LINK_DDB_ITEM,
    "anon_project_specific_user_id": "87b8f9a8-2400-4259-a8d9-a2f0b16d9ea1",
    "status": "assigned",
}
