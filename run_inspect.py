import csv
import time
from dataclasses import dataclass

from src.client import LAYER_TYPE, RestClient
from src.oauth2_provider_mock import OAuth2ProviderMock
from src import settings

USERNAME_PREFIX = 'performace_tests_'
PUBLIC_WS_PREFIX = f'{USERNAME_PREFIX}public_'
USERS = []
PUBLIC_WORKSPACES = []


@dataclass
class Publication:
    type: str
    workspace: str
    name: str
    rest_args: dict
    uuid = None


@dataclass
class WmsCapabilitiesRequest:
    actor_name: str
    exp_layer_prefixes: list


def main():
    n_cycles_per_user = 15
    n_users = 4
    n_cycles = n_cycles_per_user*n_users
    csv_file_path = 'tmp/performance.csv'

    with ((OAuth2ProviderMock())):

        client = RestClient("http://localhost:8000")

        for user_n in range(1, n_users + 1):
            username = f'{USERNAME_PREFIX}{user_n}'
            USERS.append(username)
            print(f"Reserving username {username}")
            client.ensure_reserved_username(username=username, actor_name=username)
            print(f"  Delete all user publications")
            client.delete_workspace_publications(publication_type=LAYER_TYPE, workspace=username, actor_name=username)

            public_ws_name = f'{PUBLIC_WS_PREFIX}{user_n}'
            PUBLIC_WORKSPACES.append(public_ws_name)
            print(f"  Delete all publications in public ws {public_ws_name}")
            client.delete_workspace_publications(publication_type=LAYER_TYPE, workspace=public_ws_name, actor_name=username, skip_404=True)

        all_publications = []
        cycle_n = 0

        for user_n in range(1, n_users + 1):
            username = USERS[user_n-1]
            public_ws_name = PUBLIC_WORKSPACES[user_n-1]
            for user_cycle_n in range(1, n_cycles_per_user + 1):
                cycle_n += 1
                print(f"Running cycle {cycle_n}/{n_cycles}, (user {user_n}/{n_users}, user cycle {user_cycle_n}/{n_cycles_per_user})")

                time_report = {
                    'cycle': cycle_n,
                    'user': user_n,
                    'user_cycle': user_cycle_n,
                }

                start_cycle = time.time()

                # define publications to post
                publications_to_post = [
                    Publication(type=LAYER_TYPE,
                                workspace=username,
                                name=f'private_layer_{user_cycle_n}',
                                rest_args={
                                    'access_rights': {'read': username},
                                    'actor_name': username,
                                },
                                ),
                    Publication(type=LAYER_TYPE,
                                workspace=username,
                                name=f'public_layer_{user_cycle_n}',
                                rest_args={
                                    'access_rights': {'read': 'EVERYONE'},
                                    'actor_name': username,
                                },
                                ),
                    Publication(type=LAYER_TYPE,
                                workspace=public_ws_name,
                                name=f'public_ws_layer_{user_cycle_n}',
                                rest_args={
                                    'access_rights': {'write': 'EVERYONE'},
                                    'actor_name': settings.ANONYM_USER,
                                },
                                ),
                ]

                # post publications
                start_post_publs = time.time()
                for publ in publications_to_post:
                    start_post_publ = time.time()
                    resp_json = client.post_workspace_publication(publication_type=publ.type,
                                                                  workspace=publ.workspace,
                                                                  name=publ.name,
                                                                  **publ.rest_args,
                                                                  )
                    publ.uuid = resp_json['uuid']
                    all_publications.append(publ)
                    layer_prefix = publ.name.rsplit('_', 1)[0]
                    time_report[f"post_{layer_prefix}"] = time.time() - start_post_publ
                time_report['post_all_layers'] = time.time() - start_post_publs

                # define wms capabilities requests
                wms_requests = [
                    WmsCapabilitiesRequest(actor_name=username, exp_layer_prefixes=['private_layer', 'public_layer', 'public_ws_layer_']),
                    WmsCapabilitiesRequest(actor_name=settings.ANONYM_USER, exp_layer_prefixes=['public_layer', 'public_ws_layer_']),
                ]

                # send wms capabilities requests
                start_wms_requests = time.time()
                for wms_request in wms_requests:
                    start_wms_request = time.time()
                    client.get_wms_capabilities(geoserver_workspace='layman_wms',
                                                actor_name=wms_request.actor_name)

                    time_report[f"get_wms_{wms_request.actor_name}"] = time.time() - start_wms_request
                time_report['get_all_wms'] = time.time() - start_wms_requests

                time_report['all_cycle'] = time.time() - start_cycle

                # write time report
                print(time_report)
                if cycle_n == 1:
                    with open(csv_file_path, "w", newline='', encoding='utf-8') as csv_file:
                        csv_writer = csv.DictWriter(csv_file, fieldnames=time_report.keys())
                        csv_writer.writeheader()
                        csv_writer.writerow(time_report)
                else:
                    with open(csv_file_path, "a", newline='', encoding='utf-8') as csv_file:
                        csv_writer = csv.DictWriter(csv_file, fieldnames=time_report.keys())
                        csv_writer.writerow(time_report)


if __name__ == "__main__":
    main()
