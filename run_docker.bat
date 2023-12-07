@echo off
setlocal

if "%~2"=="" (
  echo Usage: run_docker.bat ^<IRIS_IMAGE^>:^<TAG^> ^<IRIS_INSTANCE^>
  exit /b 1
)

echo FROM %1 > Dockerfile.temporary
type .\docker\Dockerfile.template >> Dockerfile.temporary
docker build -t iridescent --build-arg IRIS_INSTANCE="%2" -f Dockerfile.temporary .
docker container run --rm -it --name iridescent iridescent

endlocal
