from flask import request, url_for

from funcy import distinct, take
from itertools import chain

import re
from redash import models
from redash.permissions import require_permission, require_admin_or_owner
from redash.handlers.base import BaseResource, get_object_or_404


class RecentDashboardsResource(BaseResource):
    @require_permission('list_dashboards')
    def get(self):
        recent = [d for d in models.Dashboard.recent(self.current_org, self.current_user.groups, self.current_user.id, for_user=True)]
        temp = []
        if self.current_user.id != 1:
            for d in recent:
                if re.match('^' + self.current_user.name, d.name) != None:
                    temp.append(d)
                if self.current_user.dashlist != None or self.current_user.dashlist != '':
                    dl = self.current_user.dashlist.split(',')
                    for dash in dl:
                        if re.match('^' + dash, d.name) != None:
                            temp.append(d)
        else:
            temp = recent

        recent = [d.to_dict() for d in temp]
        return recent


class DashboardListResource(BaseResource):
    @require_permission('list_dashboards')
    def get(self):
        dashboards = [d for d in models.Dashboard.all(self.current_org, self.current_user.groups, self.current_user)]
        temp = []
        if self.current_user.id != 1:
            for d in dashboards:
                if re.match('^' + self.current_user.name, d.name) != None:
                    temp.append(d)
                if self.current_user.dashlist != None or self.current_user.dashlist != '':
                    dl = self.current_user.dashlist.split(',')
                    for dash in dl:
                        if re.match('^' + dash, d.name) != None:
                            temp.append(d)
        else:
            temp = dashboards

        dash = [d.to_dict() for d in temp]
        return dash

    @require_permission('create_dashboard')
    def post(self):
        dashboard_properties = request.get_json(force=True)
        dashboard = models.Dashboard(name=dashboard_properties['name'],
                                     org=self.current_org,
                                     user=self.current_user,
                                     layout='[]')
        dashboard.save()
        return dashboard.to_dict()


class DashboardResource(BaseResource):
    @require_permission('list_dashboards')
    def get(self, dashboard_slug=None):
        dashboard = get_object_or_404(models.Dashboard.get_by_slug_and_org, dashboard_slug, self.current_org)
        response = dashboard.to_dict(with_widgets=True, user=self.current_user)

        api_key = models.ApiKey.get_by_object(dashboard)
        if api_key:
            response['public_url'] = url_for('redash.public_dashboard', token=api_key.api_key, org_slug=self.current_org.slug, _external=True)
            response['api_key'] = api_key.api_key

        return response

    @require_permission('edit_dashboard')
    def post(self, dashboard_slug):
        dashboard_properties = request.get_json(force=True)
        # TODO: either convert all requests to use slugs or ids
        dashboard = models.Dashboard.get_by_id_and_org(dashboard_slug, self.current_org)
        dashboard.layout = dashboard_properties['layout']
        dashboard.name = dashboard_properties['name']
        dashboard.save()

        return dashboard.to_dict(with_widgets=True, user=self.current_user)

    @require_permission('edit_dashboard')
    def delete(self, dashboard_slug):
        dashboard = models.Dashboard.get_by_slug_and_org(dashboard_slug, self.current_org)
        dashboard.is_archived = True
        dashboard.save()

        return dashboard.to_dict(with_widgets=True, user=self.current_user)


class DashboardShareResource(BaseResource):
    def post(self, dashboard_id):
        dashboard = models.Dashboard.get_by_id_and_org(dashboard_id, self.current_org)
        require_admin_or_owner(dashboard.user_id)
        api_key = models.ApiKey.create_for_object(dashboard, self.current_user)
        public_url = url_for('redash.public_dashboard', token=api_key.api_key, org_slug=self.current_org.slug, _external=True)

        return {'public_url': public_url, 'api_key': api_key.api_key}

    def delete(self, dashboard_id):
        dashboard = models.Dashboard.get_by_id_and_org(dashboard_id, self.current_org)
        require_admin_or_owner(dashboard.user_id)
        api_key = models.ApiKey.get_by_object(dashboard)

        if api_key:
            api_key.active = False
            api_key.save()


