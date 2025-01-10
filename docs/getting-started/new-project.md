# Starting a new project

1. Create a project directory with `git init <MY_PROJECT_DIR>`
1. `cd <MY_PROJECT_DIR>`
1. Decide on what your first application is going to be called. We'll use
   `<APP_NAME>` as the placeholder for what you choose in the following steps.
1. Start with `template-infra` by running:
    ```sh
    nava-platform infra install --commit . <APP_NAME>
    ```
1. Then utilize one of the application templates for `<APP_NAME>` with:
    ```sh
    nava-platform app install --commit --template-uri <TEMPLATE_URI> . <APP_NAME>
    ```
1. Follow the steps in the `First time initialization` section of the generated
   `/infra/README.md` file for creating the initial resources/dev environment.
1. Once you have a dev environment created, enable a host of other features by running:
    ```sh
    nava-platform infra update --answers-only --data app_has_dev_env_setup=true .
    ```

And you're off!

