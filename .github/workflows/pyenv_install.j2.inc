{% raw %}
  pyenv:
    # Don't run twice for internal PRs from our own repo
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name != github.repository
    uses: rockandska/ga-workflows/.github/workflows/pyenv-install.yml@pyenv
{% endraw %}
