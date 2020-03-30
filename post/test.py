import os

import django
from bs4 import BeautifulSoup
from django.db.models import Max

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketWeb.settings')
django.setup()

from post.views import classification_chart, member_chart

# print(member_chart())
# for i in member_post_link:
#     print(i)
# print(echart.js_dependencies.items)
# script_list = list(echart.js_dependencies)

h = '''
<tbody>
				<tr>
					<td><i class="fa fa-plus-square green" aria-hidden="true"></i> Positive</td>
					<td class="text-center">118</td>
					<td class="text-center">211</td>
					<td class="text-center">211</td>
				</tr>
				<tr>
					<td><i class="fa fa-minus-square red" aria-hidden="true"></i> Negative</td>
					<td class="text-center">2</td>
					<td class="text-center">2</td>
					<td class="text-center">2</td>
				</tr>
			  </tbody>
'''

b = BeautifulSoup(h, 'lxml')
tr = b.select('tr')
print(tr[0].text.strip().split('\n')[1:],
      tr[1].text.strip().split('\n')[1:])
