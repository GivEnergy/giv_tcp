docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-ma:1.1.4 --push .
::docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6 -t britkat/giv_tcp-ma:2022.07.28 -t britkat/giv_tcp-ma:latest -t britkat/giv_tcp-ma:1.1.4 --push .
