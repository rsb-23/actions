# actions

common actions for all repo

## Idea

- [x] Be `zizmor` compliant
- [x] Easy version upgrade for all workflows.
- [x] Reduce duplicate workflow changes

## Usage

> [!NOTE]
> All inputs are optional, unless mentioned required

> [!TIP]
> Use @main tag to use the latest version. 

### Actions

- Checkout
    ```yaml
    - name: Checkout page branch
      uses: rsb-23/actions/checkout@main
      with:
        ref: main
        fetch-depth: 1
        fetch-tags: false
        persist-credentials: false
    ```

- Commit-n-Push
  ```yaml
  - name: Commit and push changes
    uses: rsb-23/actions/commit-n-push@main
    with:
      commit_message: "" # required
      files: "." # default= adds all files
      git_user: "action[bot]"
  ```

- Setup-Python
  ```yaml
  - name: Setup Python
    uses: rsb-23/actions/setup-python@main
    with:
      python-version: 3.12
    ```

### Workflows

- CI-Linter  
  Validates Github actions and workflows
  ```yaml
  name: CI Lint
  on:
    push:
      branches: [ main, master ]
      paths:
        - '.github/**/*.yml'
        - '.github/**/*.yaml'
  jobs:
    lint:
      uses: rsb-23/actions/.github/workflows/workflow-linter.yml@main
      permissions:
        security-events: write
      with:
        tools: actionlint,zizmor
      secrets:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  ```
