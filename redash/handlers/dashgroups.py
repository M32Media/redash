from redash import models
from redash.handlers.base import BaseResource
from redash.permissions import require_permission
from flask import request



class DashgroupList(BaseResource):
    @require_permission('admin')
    def get(self):
        return [dg.to_dict() for dg in models.Dashgroup.get_dashgroups()]
    @require_permission('admin')
    def post(self):
        return 0;


class UserDashgroupList(BaseResource):
    def get(self):
        user_dashgroups = models.UserDashgroup.get_dashgroups(self.current_user.id)

        #This is working
        return [d.to_dict() for d in user_dashgroups]
    @require_permission('admin')
    def post(self):

    	properties = request.get_json(force=True)

    	u_dg = models.UserDashgroup(user_id=properties['uid'], dashgroup_id=properties['did'])
        models.db.session.add(u_dg)
        models.db.session.commit()

        return u_dg.to_dict()

class OneUserDashgroupList(BaseResource):
    def get(self,user_id):
        user_dashgroups = models.UserDashgroup.get_dashgroups(user_id)

        #This is working
        return [d.to_dict() for d in user_dashgroups]

class DashgroupDashboardList(BaseResource):
    def get(self):
        dashgroup_dashboards = models.DashgroupDashboard.get_dashgroup_dashboards()

        print(dashgroup_dashboards)

        return [d.to_dict() for d in dashgroup_dashboards]
