from flask.cli import AppGroup
from click import argument, option
from redash import models

manager = AppGroup(help="Dashboard management commands.")

#Click prevents us from simply calling a command from another command, hence this function.
def create_dashboard_logic(old_publisher, publisher, dashboard_id):
    old_dashboard = models.Dashboard.get_by_id(dashboard_id)
    dashboardname = old_dashboard.name.lower().replace(old_publisher.lower(), publisher.lower())

    dashboard = models.Dashboard(name=dashboardname,
                                 org=models.Organization.get_by_id(1),
                                 user=models.User.get_by_id(1),
                                 dashboard_filters_enabled = old_dashboard.dashboard_filters_enabled,
                                 layout='[]')
    models.db.session.add(dashboard)
    models.db.session.commit()
    new_layout = ''
    for widget in old_dashboard.layout.replace(' ', '').replace('[', '').replace(']', '').split(','):
        old_widget = models.Widget.get_by_id(widget)
        if old_widget.visualization != None:
            query_id = old_widget.visualization.query_rel.id
            new_query_sql = create_query_definition(query_id, publisher, old_publisher)
            new_query = models.Query(
                name=old_widget.visualization.query_rel.name + ' [' + publisher.lower() + ']',
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
            new_visualisation = models.Visualization(
                type=old_widget.visualization.type,
                query_rel=new_query,
                name=old_widget.visualization.name,
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

            new_layout = new_layout + '[' + str(new_widget.id) + '],'

    new_layout = new_layout.rstrip(',')
    new_layout = '[' + new_layout + ']'

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

