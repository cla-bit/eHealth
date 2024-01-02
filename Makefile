build:
		docker-compose build

up:
		docker-compose up
		
stop:
		docker-compose stop e-health

remove:
		docker-compose rm --all -f e-health

bash:
		docker-compose run e-health bash

