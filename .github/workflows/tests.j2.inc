{% raw %}
  Tests:
    needs: pyenv

    # Don't run twice for internal PRs from our own repo
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name != github.repository

    runs-on: ubuntu-22.04
    env:
      pyenv_root: "/home/runner/.pyenv"
{% endraw %}
    strategy:
      matrix:
        target:
          {% for t in tests_targets.split(' ') -%}
          - {{ t }}
          {% endfor %}
{% raw %}
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Restore pyenv cache
        id: pyenv-cache
        uses: actions/cache/restore@v4
        env:
          cache-name: pyenv-cache
        with:
          path: ${{ env.pyenv_root }}
          key: ${{ runner.os }}-pyenv-cache-${{ hashFiles('.python-version') }}
          restore-keys: ${{ runner.os }}-pyenv-cache-

      - name: Setup PYENV
        run: |
          echo "${{ env.pyenv_root }}/bin" >> "$GITHUB_PATH"
          echo "PYENV_ROOT=${{ env.pyenv_root }}" >> "$GITHUB_ENV"

      - name: Install Tmux
        if: contains(matrix.target, 'pytest')
        run: |
          sudo apt-get install tmux

      - name: make ${{matrix.target}}
        run: |
          eval "$(pyenv init -)"
          pyenv rehash
          make ${{matrix.target}}
      - name: Check that workingtree is still clean
        run: make check-git-clean
{% endraw %}
