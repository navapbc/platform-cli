# Starting a new project

1. Create a project directory with `git init <MY_PROJECT_DIR>`
1. `cd <MY_PROJECT_DIR>`
1. Decide on what your first application is going to be called. We'll use
   `<APP_NAME>` as the placeholder for what you choose in the following steps.
1. Start with `template-infra` by running:
    ```sh
    nava-platform infra install --commit . <APP_NAME>
    ```
    This installs the base infrastructure template and an app-specific infra
    layer for `<APP_NAME>`. Copier will prompt you for project configuration
    values (project name, AWS region, etc.). When it finishes, you will have a
    populated `infra/` directory and a `.template-infra/` directory tracking
    the installed version. The `--commit` flag automatically creates a git
    commit with the generated files.
1. Then utilize one of the application templates for `<APP_NAME>` with:
    ```sh
    nava-platform app install --commit --template-uri <TEMPLATE_URI> . <APP_NAME>
    ```
    Available application template URIs:
    - Flask API: `https://github.com/navapbc/template-application-flask`
    - Next.js: `https://github.com/navapbc/template-application-nextjs`
    - Rails: `https://github.com/navapbc/template-application-rails`

    For example, to install the Flask template:
    ```sh
    nava-platform app install --commit \
      --template-uri https://github.com/navapbc/template-application-flask \
      . myapp
    ```
1. Follow the steps in the `First time initialization` section of the generated
   `/infra/README.md` file for creating the initial resources/dev environment.
1. Once you have a dev environment created, enable a host of other features by running:
    ```sh
    nava-platform infra update-app --answers-only --data app_has_dev_env_setup=true . <APP_NAME>
    ```

And you're off!

