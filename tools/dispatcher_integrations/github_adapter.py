"""GitHub source adapter; intentionally no POST, merge or model subprocess."""
if __package__:
    from .contracts import REPO, AuthorizationError, authorize_job
else:
    from contracts import REPO, AuthorizationError, authorize_job

class GitHubAdapter:
    def __init__(self,client):self.client=client
    def fetch_approved_issue(self,number,policy,now):
        if type(number) is not int or number<1:
            raise AuthorizationError('invalid issue selector')
        event=self.client.get_json('/repos/'+REPO+'/issues/'+str(number))
        if not isinstance(event,dict) or event.get('number')!=number:
            raise AuthorizationError('missing, changed or unvalidated issue response')
        return authorize_job(event,policy,now)
