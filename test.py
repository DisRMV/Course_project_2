import unittest
from vk import Admin, Group
from db import get_data
import vk_api


class TestAdmin(unittest.TestCase):

    def setUp(self):
        self.token = get_data()['Admin_token']
        self.vk = vk_api.VkApi(token=self.token)
        self.search_terms = {'age_from': 39, 'age_to': 43, 'city': 'Москва', 'sex': 2}

    def test_user_search(self):
        self.assertDictEqual(Admin.user_search(self, self.search_terms, [])[0],
                             {15681307: 'https://vk.com/id15681307'})

    def test_top_photo(self):
        list_candidates = [{502152633: 'https://m.vk.com/id502152633'}]
        top_photo_result = [{502152633: 'https://m.vk.com/id502152633', 'url_photo': [
            {457239052: 'https://sun9-81.userapi.com/impf/c858220/v858220936/e78bf/9aWMUUirxZU.jpg?size=525x1080&qua'
                        'lity=96&sign=739ac058a7be64f3f92fdc74892df2c5&c_uniq_tag=u9EeslXEWbvVzTxTwpqIOhA1C2JVWBcKqHF'
                        '3ud8MAP8&type=album'},
            {456239020: 'https://sun9-82.userapi.com/impf/c845121/v845121752/cc9d6/bUC6rWMqq1c.jpg?size=246x402&qual'
                        'ity=96&sign=c474949a190b6a73d30c2312ab6fdf1f&c_uniq_tag=gDNnl_2NP0VPARywIWwFfIyuUj6RMIkZEAu9'
                        'AhKGwPw&type=album'},
            {456239019: 'https://sun9-17.userapi.com/impf/c845121/v845121752/cc9cf/cit0AkHRBMw.jpg?size=1280x851&qual'
                        'ity=96&sign=93bd7cd19900d6328dd81eaf7362dd9c&c_uniq_tag=ycl2yXaKBXRfr894KtZGvwtdMCSiCYLKRxnT'
                        'uV6FRyQ&type=album'}]}]
        self.assertListEqual(Admin.top_photo(self, list_candidates), top_photo_result)


class TestGroup(unittest.TestCase):

    def setUp(self):
        self.token = get_data()['Group_token']
        self.vk = vk_api.VkApi(token=self.token)

    def test_get_info(self):
        result = {'age_from': 28, 'age_to': 32, 'city': 'Калуга', 'sex': 1}
        self.assertDictEqual(Group.get_info(self, user_id='138078925'), result)


if __name__ == '__main__':
    unittest.main()
