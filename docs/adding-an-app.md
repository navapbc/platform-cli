# Adding an application

## If using `template-infra`

Whether you will use an existing application template or write your own, to add
the infrastructure skeleton for hooking your application up, run:

```sh
nava-platform infra add-app . <APP_NAME>
```

## Using an application template

If you want to use one of the `template-application-` from [the
Platform](https://github.com/navapbc/platform/), run:

```sh
nava-platform app install --template-uri <TEMPLATE_URI> . <APP_NAME>
```

So for example, if you had a project utilizing the infrastructure template and
wanted to add a new application based on the rails template, you would run:

```sh
nava-platform infra add-app --commit . my-super-awesome-app
nava-platform app install --template-uri gh:navapbc/template-application-rails --commit . my-super-awesome-app
```

The `app install` part may result in a conflict in the `<APP_NAME>/Makefile`
file as the infrastructure template and the application template usually provide
a different copy. Typically you'll want to just accept the application template
version.
