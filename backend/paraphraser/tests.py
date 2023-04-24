from django.test import TestCase

# Create your tests here.

class TestAPI(TestCase):
    def setUp(self):
        self.tree = (
            "(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) (, ,) (CC or) (NP (NNP "
            + "Barri) (NNP "
            + "Gòtic) ) ) "
            + "(, ,) (VP (VBZ has) (NP (NP (JJ narrow) (JJ medieval) (NNS streets) ) (VP (VBN filled) (PP "
            + "(IN with) "
            + "(NP (NP "
            + "(JJ trendy) (NNS bars) ) (, ,) (NP (NNS clubs) ) (CC and) (NP (JJ Catalan) (NNS "
            + "restaurants) ) ) ) ) "
            + ") ) )"
        )

    def test_paraphrase_status(self):
        response = self.client.get(f"/paraphrase/?tree={self.tree}&limit=10")
        self.assertEqual(response.status_code, 200)

    def test_paraphrase_limit(self):
        response = self.client.get(f"/paraphrase/?tree={self.tree}&limit=10")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["paraphrases"]), 10)
