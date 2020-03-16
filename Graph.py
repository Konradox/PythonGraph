import adal
import requests
import time

class Graph:
    def __init__(self, tenantId, client_id, client_secret):
        if not tenantId or not client_id or not client_secret:
            print('*ERROR:{0}* tenant id, client id or client secret is empty'.format(time.time()*1000))
            raise RuntimeError('*ERROR:{0}* tenant id, client id or client secret is empty'.format(time.time()*1000))

        context = adal.AuthenticationContext("https://login.microsoftonline.com/" + tenantId)
        # Application model
        self.token = context.acquire_token_with_client_credentials("https://graph.microsoft.com", client_id, client_secret)["accessToken"]

        # Delegated authorization
        # self.token = context.acquire_token_with_username_password("https://graph.microsoft.com", username, password, client_id)["accessToken"]

    BASE_URL_V1 = 'https://graph.microsoft.com/v1.0{0}'
    BASE_URL_BETA = 'https://graph.microsoft.com/beta{0}'

    # GROUPS ========================================================

    def get_group_members_display_names(self, group_id):
        result = self.get_group_members(group_id)
        users = []
        for u in result['value']:
            users.append(u['displayName'])
            # users += u['userPrincipalName'] + ';'
        return users

    def get_group_members(self, group_id):
        return self._graph_get_call('/groups/{0}/members'.format(group_id))

    def get_group_id(self, groupName):
        group = self._graph_get_call("/groups?$filter=displayName eq '{0}'".format(groupName))
        if group and group['value'] and group['value'][0]['id']:
            return group['value'][0]['id']
        raise RuntimeError('*ERROR:{0}* Group not found'.format(time.time()*1000))

    def delete_group_by_id(self, group_id):
        return self._graph_delete_call('/groups/{0}'.format(group_id))

    def delete_group_by_name(self, group_name):
        group_id = self.get_group_id(group_name)
        self.delete_group_by_id(group_id)

    # USER ==========================================================

    def get_all_groups(self, queryParameters=''):
        return self._graph_get_call('/groups{0}'.format(queryParameters))
        
    # GENERAL =======================================================

    def _graph_delete_call(self, url):
        request_url = self.BASE_URL_V1.format(url)
        response = requests.delete(url=request_url, headers=self._get_default_headers())
        return response

    def _graph_get_call(self, url):
        request_url = self.BASE_URL_V1.format(url)
        response = requests.get(url=request_url, headers=self._get_default_headers())
        return response.json()

    def _get_default_headers(self):
        return {
            'Authorization': 'Bearer {0}'.format(self.token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }