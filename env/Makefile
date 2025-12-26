remove_env:
	rm -rf .env

set_env_prod: remove_env
	if [ -f ./env/.env.prod ]; then cat ./env/.env.prod | grep -v '^\s*#' > .env; fi

.PHONY: remove_env set_env_prod

# End Makefile