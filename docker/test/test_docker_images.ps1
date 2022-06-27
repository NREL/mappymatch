# Run from root.
# . .\docker\test\test_docker_images.ps1
docker build -f docker/test/Dockerfile_test_38  -t rowlando13/mappymatch:python_38_finish_test .
docker run --rm rowlando13/mappymatch:python_38_finish_test
docker build -f docker/test/Dockerfile_test_39  -t rowlando13/mappymatch:python_39_finish_test .
docker run --rm rowlando13/mappymatch:python_39_finish_test 
docker build -f docker/test/Dockerfile_test_310  -t rowlando13/mappymatch:python_310_finish_test .
docker run --rm rowlando13/mappymatch:python_310_finish_test
