import json

from flask import request
from redash import models
from redash.handlers.base import BaseResource
from redash.permissions import (require_access,
                                require_object_modify_permission,
                                require_permission, view_only)


class WidgetListResource(BaseResource):
    @require_permission('edit_dashboard')
    def post(self):
        """
        Add a widget to a dashboard.

        :<json number dashboard_id: The ID for the dashboard being added to
        :<json visualization_id: The ID of the visualization to put in this widget
        :<json object options: Widget options
        :<json string text: Text box contents
        :<json number width: Width for widget display

        :>json object widget: The created widget
        :>json array layout: The new layout of the dashboard this widget was added to
        :>json boolean new_row: Whether this widget was added on a new row or not
        :>json number version: The revision number of the dashboard
        """
        widget_properties = request.get_json(force=True)
        dashboard = models.Dashboard.get_by_id_and_org(widget_properties.pop('dashboard_id'), self.current_org)
        require_object_modify_permission(dashboard, self.current_user)

        widget_properties['options'] = json.dumps(widget_properties['options'])
        widget_properties.pop('id', None)
        widget_properties['dashboard'] = dashboard

        visualization_id = widget_properties.pop('visualization_id')
        if visualization_id:
            visualization = models.Visualization.get_by_id_and_org(visualization_id, self.current_org)
            require_access(visualization.query_rel.groups, self.current_user, view_only)
        else:
            visualization = None

        widget_properties['visualization'] = visualization

        widget = models.Widget(**widget_properties)
        models.db.session.add(widget)
        models.db.session.commit()

        layout = json.loads(widget.dashboard.layout)
        new_row = True


        spacer = 99
        not_spacer = 77
        #This gives the conversion between widget size number (1 being 50%, 2 being 100% and 3 being 25%)
        widget_size_to_width = {1:(2, not_spacer), 2:(4,not_spacer), 3:(1,not_spacer), -1:(1, spacer), -2:(2,spacer), -3:(3,spacer), -4:(4,spacer)}
        widget_width = widget_size_to_width[widget.width][0]
        #Index of the new widget in the layout columns.
        new_widget_idx = -1

        #If there is no visualization or the widgets size is full length
        if len(layout) == 0 or widget_width == 4:
            new_widget_idx = len(layout)
            layout.append([widget.id])

        else:
            #else, we try to find a hole big enough for our widget to fit

            #thats a pretty long line... It gives us a 2d array of [[(widget_width, isSpacer), ... ], [ ... ]]
            widget_width_rows = [[widget_size_to_width[models.Widget.get_by_id(widget_id).width] if widget_id > 0 else widget_size_to_width[widget_id] for widget_id in widget_ids] for widget_ids in layout]
            #we need this to know if a row id full.
            row_sizes = [reduce((lambda x, y: x + y[0]), w_w, 0) for w_w in widget_width_rows]
            #This bit of code tries to find a spacer that's big enough to put the widget in or a row
            #that isn't full.
            for i, widget_width_row in enumerate(widget_width_rows):
                found = False
                for j, widg in enumerate(widget_width_row):
                    #If there is a spacer and its big enough
                    if widg[1] == spacer and widg[0] >= widget_width:
                        old_spacer = layout[i][j]
                        layout[i][j] = widget.id
                        #If the spacer was bigger than the widget, we add a new spacer after the new widget.
                        if widg[0] - widget_width > 0:
                            layout[i].insert(j + 1, - (widg[0] - widget_width))
                        found = True
                        #We don't need a new row if we've found a space.
                        new_row = False
                        new_widget_idx = [i, j]
                        break
                #if a space was found, we're done.
                if found:
                    break
                elif row_sizes[i] + widget_width <= 4:
                    #If a space wasn't found and the row isn't full, append it at the end and break.
                    layout[i].append(widget.id)
                    new_widget_idx = [i, len(layout[i])]
                    new_row = False
                    break

            #if we have not found a hole, put the thing in a new row.
            if new_row:
                new_widget_idx = len(layout)
                layout.append([widget.id])


        widget.dashboard.layout = json.dumps(layout)
        models.db.session.add(widget.dashboard)
        models.db.session.commit()
        return {'widget': widget.to_dict(), 'layout': layout, 'new_row': new_row, 'new_widget_idx' : new_widget_idx, 'version': dashboard.version}


class WidgetResource(BaseResource):
    @require_permission('edit_dashboard')
    def post(self, widget_id):
        """
        Updates a widget in a dashboard.
        This method currently handles Text Box widgets only.

        :param number widget_id: The ID of the widget to modify

        :<json string text: The new contents of the text box
        """
        widget = models.Widget.get_by_id_and_org(widget_id, self.current_org)
        require_object_modify_permission(widget.dashboard, self.current_user)
        widget_properties = request.get_json(force=True)
        widget.text = widget_properties['text']
        models.db.session.commit()
        return widget.to_dict()

    @require_permission('edit_dashboard')
    def delete(self, widget_id):
        """
        Remove a widget from a dashboard.

        :param number widget_id: ID of widget to remove

        :>json array layout: New layout of dashboard this widget was removed from
        :>json number version: Revision number of dashboard
        """
        widget = models.Widget.get_by_id_and_org(widget_id, self.current_org)
        require_object_modify_permission(widget.dashboard, self.current_user)
        widget.delete()
        models.db.session.commit()
        return {'layout': widget.dashboard.layout, 'version': widget.dashboard.version}
