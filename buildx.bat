::docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-dev:dev2 --push .
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-dev:dev2 -t britkat/giv_tcp-dev:2.1.34 --push .
