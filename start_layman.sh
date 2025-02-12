#!/bin/bash

set -exu

pushd ../layman
make stop-and-remove-all-docker-containers || true
make reset-data-directories || true

# start Layman with oauth2_provider_mock authentication
cp .env.dev .env
sed -i -e "s/OAUTH2_INTROSPECTION_URL=.*/OAUTH2_INTROSPECTION_URL=http:\\/\\/host.docker.internal:8123\\/rest\\/test-oauth2\\/introspection?is_active=true/" .env
sed -i -e "s/OAUTH2_USER_PROFILE_URL=.*/OAUTH2_USER_PROFILE_URL=http:\\/\\/host.docker.internal:8123\\/rest\\/test-oauth2\\/user-profile/" .env
make start-dev
docker logs -f layman_dev 2>&1 | sed '/Layman successfully started/ q'
popd
