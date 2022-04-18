# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ### pip install arrow

# +
import Dual
from datetime import datetime
import arrow


today = arrow.now()
three_months_ago = today.shift(months=-3)

today = today.strftime('%Y-%m-%d')
three_months_ago = three_months_ago.strftime('%Y-%m-%d')
