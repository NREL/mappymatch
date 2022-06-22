# Run from root.
# . .\docker\build\build_docker_images.ps1
docker build -f docker/build/Dockerfile_build_38 -t rowlando13/mappymatch:python_38_base_test ./docker 
docker push rowlando13/mappymatch:python_38_base_test
docker build -f docker/build/Dockerfile_build_39 -t rowlando13/mappymatch:python_39_base_test ./docker
docker push rowlando13/mappymatch:python_39_base_test
docker build -f docker/build/Dockerfile_build_310 -t rowlando13/mappymatch:python_310_base_test ./docker
docker push rowlando13/mappymatch:python_310_base_test