{% raw %}
  Tests:
    needs: pyenv
    runs-on: *UBUNTU_IMAGE
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
        with:
          path: ${{ needs.pyenv.outputs.cache-path }}
          key: ${{ needs.pyenv.outputs.cache-key }}
          restore-keys: ${{ needs.pyenv.outputs.cache-restore-keys }}

      - name: Setup PYENV
        run: |
          echo "${{ needs.pyenv.outputs.cache-path }}/bin" >> "$GITHUB_PATH"
          echo "PYENV_ROOT=${{ needs.pyenv.outputs.cache-path }}" >> "$GITHUB_ENV"

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
