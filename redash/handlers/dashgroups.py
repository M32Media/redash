from redash import models
from redash.handlers.base import BaseResource
from redash.permissions import require_permission


class DashgroupList(BaseResource):
    @require_permission('admin')
    def get(self):
        return [dg.to_dict() for dg in models.Dashgroup.get_dashgroups()]

class UserDashgroupList(BaseResource):
    def get(self):
        user_dashgroups = models.UserDashgroup.get_dashgroups(self.current_user.id)

        #This is working
        return [d.to_dict() for d in user_dashgroups]

class OneUserDashgroupList(BaseResource):
    def get(self,user_id):
        user_dashgroups = models.UserDashgroup.get_dashgroups(user_id)

        #This is working
        return [d.to_dict() for d in user_dashgroups]