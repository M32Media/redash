import json


import click
from flask.cli import FlaskGroup, run_command
from flask import current_app

from random import randint
from redash import create_app, settings, __version__
from redash.cli import users, groups, database, data_sources, organization, dashboard
from redash.monitor import get_status
from redash.tasks import refresh_queries
from redash import models
from subprocess import call

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
def version():
    """Displays Redash version."""
    print __version__

@manager.command()
def refresh_all_the_queries():
    refresh_queries()

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
@click.argument('old_publisher')
@click.argument('publishers')
@click.argument('dashboard_type', required=False)
def clone_dashboards(old_publisher, publishers, dashboard_type=None):

    dashgroup = models.Dashgroup.query.filter(models.Dashgroup.name == old_publisher).one()

    if dashgroup is None:
        print("Can't find the publisher name")
        return
    dashboard_ids = [db.dashboard_id for db in models.DashgroupDashboard.get_by_dashgroup_id(dashgroup.id)]

    #for every dashboards in the old publishers dashgroup, copy these dashboards with the new publisher
    publishers = publishers.split(',')
    dashboard_type = dashboard_type.split(',') if dashboard_type is not None else dashboard_type
    for publisher in publishers:
        for dashboard_id in dashboard_ids:
            # If we want to restrain copy to a certain type (where a type is defined in the naming convention of a dashboard
            # publisher:type:name we check if the type fits, if it doesnt, we don't copy it.
            if (dashboard_type is not None and models.Dashboard.get_by_id(dashboard_id).name.split(":")[1] not in dashboard_type):
                continue

            created = dashboard.create_dashboard_logic(old_publisher, publisher, dashboard_id)
            #we want to put the created dashboard in a new dashgroup or one that has the right name
            new_pub_group = models.Dashgroup.create_or_get_dashgroup(publisher)
            grouping = models.DashgroupDashboard(dashboard_id=created.id, dashgroup_id=new_pub_group)
            models.db.session.add(grouping)
            models.db.session.commit()


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

