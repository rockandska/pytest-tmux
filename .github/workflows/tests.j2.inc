    runs-on: ubuntu-18.04
    strategy:
      matrix:
        target:
          {% for t in tox_targets.split(' ') -%}
          - {{ t }}
          {% endfor %}
        include:
          {% for t in tox_targets.split(' ') -%} 
          - target: {{ t }}
            {%- if 'python' in t %}
            python-version: |
              {{ base_python_version }}
              {{ t | replace( tox_targets_prefix + '-python','') }}
            {%- else %}
            python-version: |
              {{ base_python_version }}
            {%- endif %}
          {% endfor -%}
{% raw %}
    steps:
      - uses: actions/checkout@v2
      - name: Install Python
        uses: actions/setup-python@v4
        with:
          python-version: |
            ${{ matrix.python-version }}
      - name: Install Tmux
        if: contains(matrix.target, 'python')
        run: |
          sudo apt-get install tmux
      - name: make ${{matrix.target}}
        run: make ${{matrix.target}}
      - name: Check that workingtree is still clean
        run: make check-git-clean
{% endraw %}
