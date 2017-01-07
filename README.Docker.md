Using AssetHub in Docker
========================

You can find Dockerfile in this repository. However, since web application
engine uses database, and the site should have some secret data, like database
passwords and so on, running it is not so simple as one docker run.

So the suggested way of running AssetHub in docker is:

1. Run postgresql container (I assume that postgres is used as DB, though
   Django allows to use other RDBMS).
2. Take files `email_settings.py.template` and `secret_settings.py.template` as
   examples and create your own `email_settings.py` and `secret_settings.py` with
   your passwords and so on.
3. Build assethub docker image with usual `docker build -t assethub .`
4. Set up initial database by running install-database.sh in container:

    ```
    docker run --rm -it --link docker_postgresql_1:postgresql \
      -e DJANGO_SUPERUSER_EMAIL='root@example.com' \
      -e DJANGO_SUPERUSER_PASSWORD='PASWORD' \
      -v ~/secret_settings.py:/assethub/assethub/secret_settings.py \
      -v ~/email_settings.py:/assethub/assethub/email_settings.py \
        assethub /install-database.sh
    ```

5. Now you can run the AssetHub instance:

    ```
    docker run -d --name assethub -it --link docker_postgresql_1:postgresql \
      -p 127.0.0.1:8000:8000 \
      -v ~/secret_settings.py:/assethub/assethub/secret_settings.py \
      -v ~/email_settings.py:/assethub/assethub/email_settings.py \
        assethub
    ```

6. Now AssetHub is available at http://localhost:8000. Use nginx or other
   frontend to publish it to real web and probably enable HTTPS support.

