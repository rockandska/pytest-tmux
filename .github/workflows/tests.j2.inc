    runs-on: ubuntu-22.04
    strategy:
      matrix:
        target:
          {% for t in tox_targets.split(' ') -%}
          - {{ t }}
          {% endfor %}
        include:
          {% for t in tox_targets.split(' ') -%} 
          - target: {{ t }}
            {%- if t.startswith(tox_targets_prefix + '-py') %}
            {%- set t = t.replace( tox_targets_prefix + '-py','') %}
            python-version: |
              {{ base_python_version }}
              {{ t[:t.index('-')]  }}
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
        if: contains(matrix.target, 'pytest')
        run: |
          sudo apt-get install tmux
      - name: make ${{matrix.target}}
        run: make ${{matrix.target}}
      - name: Check that workingtree is still clean
        run: make check-git-clean
{% endraw %}
