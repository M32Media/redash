import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import click
from flask.cli import FlaskGroup, run_command
from flask import current_app
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from random import randint
from redash import create_app, settings, __version__
from redash.cli import users, groups, database, data_sources, organization, dashboard
from redash.monitor import get_status
import redash.tasks
from redash.tasks import refresh_queries, refresh_selected_queries
from redash import models
from subprocess import call
import json
from subprocess import check_output
import csv
import os
import binascii

from funcy import project

def create(group):
    app = current_app or create_app()
    group.app = app

    @app.shell_context_processor
    def shell_context():
        from redash import models
        return dict(models=models)

    return app


@click.group(cls=FlaskGroup, create_app=create)
def manager():
    """Management script for Redash"""

manager.add_command(database.manager, "database")
manager.add_command(users.manager, "users")
manager.add_command(groups.manager, "groups")
manager.add_command(data_sources.manager, "ds")
manager.add_command(organization.manager, "org")
manager.add_command(dashboard.manager, "dashboard")
manager.add_command(run_command, "runserver")

@manager.command()
@click.argument('month_to_change')
def clone_month(month_to_change):

    # Check whether the month is correct
    try:
        date_old = datetime.strptime(month_to_change, '%Y-%m').strftime('%Y%m')
        date_new = (
            datetime.strptime(month_to_change, '%Y-%m')
            + relativedelta(months=1)).strftime('%Y%m')
    except Exception as e:
        print(e)
        print('Specify a month in the format YYYY-MM')
        return

    # Get the queries for the views of a certain publisher
    dashboard_ids = [
        db.id for db in models.Dashboard.query.all()
        if not 'Global' in db.name]

    for dashboard_id in dashboard_ids:

        dashboard = models.Dashboard.get_by_id(dashboard_id)
        print('Working on dashboard {}'.format(dashboard.name))

        layout_list = json.loads(dashboard.layout)
        new_layout = [[] for i in range(len(layout_list))]
        row_labeled_layout = [
            (layout_list[i][j], i)
            for i
            in range(len(layout_list)) for j in range(len(layout_list[i]))]

        widgets = [
            models.Widget.get_by_id(widget_ref[0])
            for widget_ref in row_labeled_layout if not widget_ref[0] < 0]
        viz_names = [
            widget.visualization.name for widget in widgets]

        for widget in row_labeled_layout:

            # Covers the case where the widget is a spacer.
            if widget[0] < 0:
                new_layout[widget[1]].append(widget[0])
                continue
            else:
                widget_to_clone = models.Widget.get_by_id(widget[0])
                new_layout[widget[1]].append(widget_to_clone.id)

            if widget_to_clone.visualization != None:
                visualization_name = widget_to_clone.visualization.name
                if date_old in visualization_name:
                    print('Visualization -> {} can be cloned from {} to {}'.format(
                        visualization_name, date_old, date_new))
                else:
                    # No need to modify the visualization, as it doesn't
                    # contain the date we are looking for
                    continue

                new_visualisation_name = widget_to_clone.visualization.name.replace(date_old, date_new)

                if new_visualisation_name in viz_names:
                    print('Visualization {} already exists'.format(new_visualisation_name))
                    continue

                query_id = widget_to_clone.visualization.query_rel.id
                query = models.Query.get_by_id(query_id)
                new_query_sql = query.query_text.replace(date_old, date_new)
                new_query_name = widget_to_clone.visualization.query_rel.name.replace(date_old, date_new)
                new_query = models.Query(
                    name=new_query_name, description='', query_text=new_query_sql,
                    user=models.User.get_by_id(1), is_archived=False,
                    schedule=None, data_source=widget_to_clone.visualization.query_rel.data_source,
                    org=models.Organization.get_by_id(1))
                models.db.session.add(new_query)
                models.db.session.commit()

                new_visualisation = models.Visualization(
                    type=widget_to_clone.visualization.type,
                    query_rel=new_query, name=new_visualisation_name,
                    fr_name=widget_to_clone.visualization.fr_name,
                    description='', options=widget_to_clone.visualization.options)

                models.db.session.add(new_visualisation)
                models.db.session.commit()
                new_widget = models.Widget(
                    type=widget_to_clone.type,
                    width=widget_to_clone.width,
                    options=widget_to_clone.options,
                    dashboard=dashboard,
                    visualization=new_visualisation)

                models.db.session.add(new_widget)
                models.db.session.commit()

                print('Created new widget {widget} for dashboard {dashboard}'.format(
                    widget=new_widget, dashboard=dashboard.name))

                #Appends the widgets id at the same row as the original.
                new_layout[widget[1]].append(new_widget.id)


        new_layout = json.dumps(new_layout).replace(' ', '')

        dashboard.layout = new_layout
        models.db.session.commit()

    models.db.session.commit()

@manager.command()
def version():
    """Displays Redash version."""
    print __version__

@manager.command()
def refresh_all_the_queries():
    refresh_queries()

@manager.command()
@click.argument('months', default=datetime.now().strftime('%Y%m'))
@click.argument('publishers', default='ALL')
@click.option(
    '--global-queries', '-gq', is_flag=True,
    help='Execute global queries too (Global dashboard)')
@click.option(
    '--non-monthly-publisher-queries', '-nmpq', is_flag=True,
    help='Execute global publisher queries too (Publisher queries that don\'t depend on the month)')
@click.option(
    '--no-query-execution', '-nqe', is_flag=True,
    help='Don\'t run queries, just return the text')
def refresh_only_selected_queries(months, publishers, global_queries, non_monthly_publisher_queries, no_query_execution):
    redash.tasks.refresh_selected_queries(
        months=months.split(','), publishers=publishers.split(','),
        global_queries=global_queries,
        non_monthly_publisher_queries=non_monthly_publisher_queries,
        no_query_execution=no_query_execution)

@manager.command()
def status():
    print json.dumps(get_status(), indent=2)

@manager.command()
def refresh_url_tags():
    models.Visualization.update_url_tags()
    print("Tags Updated")
@manager.command()
def check_settings():
    """Show the settings as Redash sees them (useful for debugging)."""
    for name, item in settings.all_settings().iteritems():
        print "{} = {}".format(name, item)

@manager.command()
@click.argument('outfile_name')
def dump_database(outfile_name):
    with open(outfile_name, 'w') as out:
        call(["pg_dump","redash"], stdout=out)

@manager.command()
@click.argument('infile_name')
def restore_database(infile_name):
    #random integer after backup to avoid overwriting anything.
    with open("db_backup_{}".format(randint(0, 100000000000)), 'w') as backup:
        call(["pg_dump","redash"], stdout=backup)
    with open(infile_name, 'r') as dump:
        call(["dropdb","redash"])
        call(["createdb","redash"])
        call(["psql", "redash"], stdin=dump)

@manager.command()
@click.argument('infile')
def make_users_from_file(infile):
    """The infile should be of the format : email, permission_group, dashgroup1;dashgroup2 , type1;type2
    Right now, the types are unsupported. permission_group is an int that is the id of the group."""
    csv_users = csv.reader(open(infile))
    for user in csv_users:
        pwd = binascii.hexlify(os.urandom(11)).decode("utf-8")
        dashgroups = user[2].replace(";",",") if user[3] == "all" else ",".join(["{}.{}".format(publisher, dashtype) for publisher in user[2].split(';') for dashtype in user[3].split(";")])
        users.create_user_logic(email=user[0], name=user[0].split("@")[0], groups=user[1], password=pwd, dashgroups=dashgroups)
        with open("generated_users", "a") as generated_user_file:
            generated_user_file.write("{},{}\n".format(user[0], pwd))

def create_subdashgroups_logic(publisher_names):
    for publisher in publisher_names:
        models.Dashgroup.get_by_name(publisher)
        dashgroup = models.Dashgroup.get_by_name(publisher)
        # this gets all the dashboards associated with a dashgroup.
        all_dashboards = [models.Dashboard.get_by_id(dgdb.dashboard_id) for dgdb in list(models.DashgroupDashboard.query.filter(models.DashgroupDashboard.dashgroup_id == dashgroup.id))]
        for dashboard in all_dashboards:
            # If the dashboard does not follow the naming convention, alerts the user and skips it.
            if len(dashboard.name.split(":")) < 3:
                print("The dashboard {} has a non compliant name. Skipping it.".format(dashboard.name))
                continue
            name = "{}.{}".format(publisher, dashboard.name.split(":")[1])
            new_dashgroup = models.Dashgroup.get_by_name(name)
            if new_dashgroup is None:
                # if its none, we need to create it.
                new_dashgroup = models.Dashgroup(name=name)
                # We need to commit and add to have an id for the association
                models.db.session.add(new_dashgroup)
                models.db.session.commit()
            new_dashgroup_dashboard = models.DashgroupDashboard(dashboard_id=dashboard.id, dashgroup_id=new_dashgroup.id)
            models.db.session.add(new_dashgroup_dashboard)
            models.db.session.commit()


@manager.command()
@click.argument("publisher_names")
def create_subdashgroups(publisher_names):
    """if a dashgroup pubX contains two dashboards: pubX:cat1:dash1 and pubX:cat2:dash1
    This command will split the dashgroup. publisher_names is a comma separated list of publishers."""
    create_subdashgroups_logic(publisher_names.split(','))


@manager.command()
@click.argument('old_publisher')
@click.argument('publishers')
@click.argument('check-portal-type', required=False)
@click.argument('check-for-cxense', required=False)
@click.argument('dashboard_type', required=False)
def clone_dashboards(old_publisher, publishers, check_portal_type=True, check_for_cxense=True, dashboard_type=None):
    # click ignores default values in unrequired arguments
    check_portal_type = check_portal_type.lower() != "false" if check_portal_type is not None else True
    check_for_cxense = check_for_cxense.lower() != "false" if check_for_cxense is not None else True
    dashgroup = models.Dashgroup.query.filter(models.Dashgroup.name == old_publisher).one()

    if dashgroup is None:
        print("Can't find the publisher name")
        return
    dashboard_ids = [db.dashboard_id for db in models.DashgroupDashboard.get_by_dashgroup_id(dashgroup.id)]

    #for every dashboards in the old publishers dashgroup, copy these dashboards with the new publisher
    publishers = publishers.split(',')
    dashboard_type = dashboard_type.split(',') if dashboard_type is not None else dashboard_type
    for publisher in publishers:
        portal_type = None
        has_cx = False
        # There are two portal types: Ad Operations and Monetization. We go check for
        # that in bq.
        if check_portal_type:
            try:
                portal_type = check_output(["bq", "query", "--format=json", 'SELECT Portal_Type FROM [adoperationsprd2:M32_Services_REF.SiteMapping] where BQ_Dataset_Name = "{}" LIMIT 1'.format(publisher)])
                # this is a bit ugly but it works
                portal_type = json.loads(portal_type.split("\n")[-2])[0]["Portal_Type"]
            except Exception as e:
                print("*********** Either {} was not found in BQ or an error occured. The publisher is going to have all possible subdashboards.***********)".format(publisher))
                print("*********** If you want to bypass that check, add false after the list of publishers ***********")
                print("This is the exception: ".format(e))
                portal_type = None
        if check_for_cxense:
            try:
                has_cx = check_output(["bq", "query", "--format=json", 'SELECT Site_ID_CX FROM [adoperationsprd2:M32_Services_REF.SiteMapping] WHERE BQ_Dataset_Name="{}" GROUP BY BQ_Dataset_Name, Site_ID_CX ORDER BY Site_ID_CX DESC LIMIT 1'.format(publisher)])
                # this is a bit ugly but it works
                has_cx = json.loads(has_cx.split("\n")[-2])[0]["Site_ID_CX"] != ""
            except Exception as e:
                print("*********** Either {} was not found in BQ or an error occured. The publisher will be consider to not have cxense.***********)".format(publisher))
                print("This is the exception: ".format(e))
                has_cx = False
        for dashboard_id in dashboard_ids:
            # If we want to restrain copy to a certain type (where a type is defined in the naming convention of a dashboard
            # publisher:type:name we check if the type fits, if it doesnt, we don't copy it.
            #if (dashboard_type is not None and models.Dashboard.get_by_id(dashboard_id).name.split(":")[1] not in dashboard_type):
            #    continue
            # If the portal type is monetization and the dashboard type is 'publisher' we don't want it.
            #elif portal_type == "Monetization" and models.Dashboard.get_by_id(dashboard_id).name.split(":")[1] == "publisher":
            #    continue
            # If the publisher doesn't have cXense, don't clone
            #elif not has_cx and models.Dashboard.get_by_id(dashboard_id).name.split(":")[1] == "cXense":
            #    continue

            created = dashboard.create_dashboard_logic(old_publisher, publisher, dashboard_id)
            #we want to put the created dashboard in a new dashgroup or one that has the right name
            new_pub_group = models.Dashgroup.create_or_get_dashgroup(publisher)
            grouping = models.DashgroupDashboard(dashboard_id=created.id, dashgroup_id=new_pub_group)
            models.db.session.add(grouping)
            models.db.session.commit()

    # We also want to create subdashgroups for all these new groups.
    #create_subdashgroups_logic(publishers)


@manager.command()
@click.argument('email', default=settings.MAIL_DEFAULT_SENDER, required=False)
def send_test_mail(email=None):
    """
    Send test message to EMAIL (default: the address you defined in MAIL_DEFAULT_SENDER)
    """
    from redash import mail
    from flask_mail import Message

    if email is None:
        email = settings.MAIL_DEFAULT_SENDER

    mail.send(Message(subject="Test Message from Redash", recipients=[email],
                      body="Test message."))
