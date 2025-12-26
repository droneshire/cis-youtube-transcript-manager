remove_env:
	rm -rf .env

set_env_prod: remove_env
	if [ -f ./env/.env.prod ]; then cat ./env/.env.common ./env/.env.prod ./env/.env.backend | grep -v '^\s*#' > .env; fi

.PHONY: remove_env
.PHONY: set_env_prod

# End Makefile