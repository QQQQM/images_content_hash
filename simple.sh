#!/usr/bin/env bash
for cmd in curl jq go; do
	if ! command -v $cmd &>/dev/null; then
		echo >&2 "error: \"$cmd\" not found!"
		exit 1
	fi
done

shift || usage 1 >&2

registryBase='https://registry-1.docker.io'
authBase='https://auth.docker.io'
authService='registry.docker.io'

imageTag="$1"
shift
image="${imageTag%%[:@]*}"
imageTag="${imageTag#*:}"
digest="${imageTag##*@}"

# add prefix library if passed official image
if [[ "$image" != *"/"* ]]; then
    image="library/$image"
fi

token="$(curl -fsSL "$authBase/token?service=$authService&scope=repository:$image:pull" | jq --raw-output '.token')"

manifestJson="$(
    curl -fsSL \
        -H "Authorization: Bearer $token" \
        -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
        -H 'Accept: application/vnd.docker.distribution.manifest.list.v2+json' \
        -H 'Accept: application/vnd.docker.distribution.manifest.v1+json' \
        "$registryBase/v2/$image/manifests/$digest"
)"
echo $manifestJson