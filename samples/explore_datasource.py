####
# This script demonstrates how to use the Tableau Server Client
# to interact with datasources. It explores the different
# functions that the Server API supports on datasources.
#
# With no flags set, this sample will query all datasources,
# pick one datasource and populate its connections, and update
# the datasource. Adding flags will demonstrate the specific feature
# on top of the general operations.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():

    parser = argparse.ArgumentParser(description='Explore datasource functions supported by the Server API.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--publish', '-p', metavar='FILEPATH', help='path to datasource to publish')
    parser.add_argument('--download', '-d', metavar='FILEPATH', help='path to save downloaded datasource')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')

    args = parser.parse_args()

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # SIGN IN
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server)
    with server.auth.sign_in(tableau_auth):
        # Query projects for use when demonstrating publishing and updating
        all_projects, pagination_item = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        # Publish datasource if publish flag is set (-publish, -p)
        if args.publish:
            if default_project is not None:
                new_datasource = TSC.DatasourceItem(default_project.id)
                new_datasource = server.datasources.publish(
                    new_datasource, args.publish, TSC.Server.PublishMode.Overwrite)
                print("Datasource published. ID: {}".format(new_datasource.id))
            else:
                print("Publish failed. Could not find the default project.")

        # Gets all datasource items
        all_datasources, pagination_item = server.datasources.get()
        print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
        print([datasource.name for datasource in all_datasources])

        if all_datasources:
            # Pick one datasource from the list
            sample_datasource = all_datasources[0]

            # Populate connections
            server.datasources.populate_connections(sample_datasource)
            print("\nConnections for {}: ".format(sample_datasource.name))
            print(["{0}({1})".format(connection.id, connection.datasource_name)
                   for connection in sample_datasource.connections])


if __name__ == '__main__':
    main()
