from flask.cli import AppGroup
from click import argument, option
from redash import models
import json

manager = AppGroup(help="Dashboard management commands.")

#Click prevents us from simply calling a command from another command, hence this function.
def create_dashboard_logic(old_publisher, publisher, dashboard_id):
    old_dashboard = models.Dashboard.get_by_id(dashboard_id)
    dashboardname = old_dashboard.name.replace(old_publisher, publisher)
    dashboardfr_name = old_dashboard.fr_name.replace(old_publisher, publisher)

    dashboard = models.Dashboard(name=dashboardname,
                               fr_name=dashboardfr_name,
                               org=models.Organization.get_by_id(1),
                               user=models.User.get_by_id(1),
                               dashboard_filters_enabled = old_dashboard.dashboard_filters_enabled,
                               layout='[]',
                               is_draft=old_dashboard.is_draft)
    models.db.session.add(dashboard)
    models.db.session.commit()
    json.dumps
    layout_list = json.loads(old_dashboard.layout)
    # List of (widget_id, row_num) to copy the old layout to the new.
    row_labeled_layout = [ (layout_list[i][j], i) for i in range(len(layout_list)) for j in range(len(layout_list[i]))]
    # We create a new list with as many empty lists as the origi
    new_layout = [[] for i in range(len(layout_list))]
    for widget in row_labeled_layout:
        # Covers the case where the widget is a spacer.
        if widget[0] < 0:
            new_layout[widget[1]].append(widget[0])
        else :
            old_widget = models.Widget.get_by_id(widget[0])
            if old_widget.visualization != None:
                query_id = old_widget.visualization.query_rel.id
                new_query_sql = create_query_definition(query_id, publisher, old_publisher)
                new_query_name= old_widget.visualization.query_rel.name.replace(old_publisher.lower(),publisher.lower())
                new_query = models.Query(
                    name=new_query_name ,
                    description='',
                    query_text=new_query_sql,
                    user=models.User.get_by_id(1),
                    is_archived=False,
                    schedule=None,
                    data_source=old_widget.visualization.query_rel.data_source,
                    org=models.Organization.get_by_id(1)
                )
                models.db.session.add(new_query)
                models.db.session.commit()
                new_visualisation_name = old_widget.visualization.name.replace(old_publisher.lower(),publisher.lower())
                new_visualisation = models.Visualization(
                    type=old_widget.visualization.type,
                    query_rel=new_query,
                    name=new_visualisation_name,
                    fr_name=old_widget.visualization.fr_name,
                    description='',
                    options=old_widget.visualization.options
                )

                models.db.session.add(new_visualisation)
                models.db.session.commit()

                new_widget = models.Widget(
                    type=old_widget.type,
                    width=old_widget.width,
                    options=old_widget.options,
                    dashboard=dashboard,
                    visualization=new_visualisation
                )

                models.db.session.add(new_widget)
                models.db.session.commit()

                #Appends the widgets id at the same row as the original.
                new_layout[widget[1]].append(new_widget.id)


    new_layout = json.dumps(new_layout).replace(' ', '')

    dashboard.layout = new_layout
    models.db.session.commit()
    return dashboard


@manager.command()
@argument('old_publisher')
@argument('publisher')
@argument('dashboard_id')
def create_dashboard(old_publisher, publisher, dashboard_id):
    create_dashboard_logic(old_publisher, publisher, dashboard_id)

def create_query_definition(id,publisher,old_publisher):
    query = models.Query.get_by_id(id)
    return query.query_text.replace(old_publisher,publisher)


