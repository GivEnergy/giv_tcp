docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-dev:dev2 --push .
::docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-ma:2.0.7 --push .
::docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-ma:latest -t britkat/giv_tcp-ma:2.0.7 --push .
