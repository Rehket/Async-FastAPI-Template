$env:PYTHONUNBUFFERED="1"
$env:PYTHONPATH=$PSScriptRoot # Used to tell python where stuff is.
$env:SERVER_NAME="localhost"
$env:SERVER_HOST="localhost"
$env:BACKEND_CORS_ORIGINS="http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8000"
$env:PROJECT_NAME="integrator"
$env:SENTRY_DSN=""
$env:POSTGRES_SERVER="localhost"
$env:POSTGRES_DB="integrator"
$env:POSTGRES_PORT="5500"
$env:POSTGRES_PASSWORD="PG+change_password"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_SCHEMA="schema_case"
$env:SECRET_KEY=")u!_Secret_So_Secret_(a1(\=%5c7ga(ou@_b_"
$env:DEBUG_MODE="True"
$env:LOCAL_DEV="True"
$env:FIRST_SUPERUSER="adam@adam.com"
$env:FIRST_SUPERUSER_PASSWORD="44d339666"
$env:USERS_OPEN_REGISTRATION="true"


# Set this ot the location of the Cert if you get a cert error
# $env:PIP_CERT="$PSScriptRoot\OD_Root_CA.crt"