from flask_script import Manager
from redash import models

manager = Manager(help="Organization management commands.")


@manager.option('publisher', help="the name of the publisher")
@manager.command
def create_dashboard(publisher,dashboard_id):
    organization = models.Organization.query().first()
    # the base model is the one from Fanoweb
    old_publisher='Fanoweb'
    old_dashboard = models.Dashboard.get_by_id(dashboard_id)
    dashboardname = old_dashboard.name.lower().replace(old_publisher.lower(), publisher.lower())
    dashboard = models.Dashboard(name=dashboardname,
                                 org=1,
                                 user=1,
                                 dashboard_filters_enabled = old_dashboard.dashboard_filters_enabled,
                                 layout='[]')
    models.db.session.add(dashboard)
    models.db.session.commit()
    new_layout = ''
    for widget in old_dashboard.layout.replace(' ', '').replace('[', '').replace(']', '').split(','):
        old_widget = models.Widget.get_by_id(widget)
        if old_widget.visualization !=None:
            query_id = old_widget.visualization.query.id
            new_query_sql = create_query_definition(query_id, publisher, old_publisher)
            new_query = models.Query(
                name=old_widget.visualization.query.name + ' [' + publisher.lower() + ']',
                description='',
                query=new_query_sql,
                user=1,
                is_archived=False,
                schedule=None,
                data_source=old_widget.visualization.query.data_source,
                org=1
            )
            models.db.session.add(query)
            models.db.session.commit()
            new_visualisation = models.Visualization(
                type=old_widget.visualization.type,
                query=new_query.id,
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
                dashboard=dashboard.id,
                visualization=new_visualisation.id
            )

            models.db.session.add(new_widget)
            models.db.session.commit()

            new_layout = new_layout + '[' + str(new_widget.id) + '],'

    new_layout = new_layout.rstrip(',')
    new_layout = '[' + new_layout + ']'

    dashboard.layout = new_layout
    models.db.session.commit()
    print 'dashboard created'

def create_query_definition(id,publisher,old_publisher):
    query = models.Query.get_by_id(id)
    return query.query.replace(old_publisher,publisher)
