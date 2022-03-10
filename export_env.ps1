conda env export | findstr -v "prefix" > conda_env.yml
conda env export --from-history | findstr -v "prefix" > conda_env_history.yml
