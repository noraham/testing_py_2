import unittest

from party import app
from model import db, example_data, connect_to_db


class PartyTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("board games, rainbows, and ice cream sundaes", result.data)

    def test_no_rsvp_yet(self):
        result = self.client.get("/")
        self.assertIn("<h2>Please RSVP</h2>", result.data)
        self.assertNotIn("<h2>Party Details</h2>", result.data)

    def test_rsvp(self):
        result = self.client.post("/rsvp",
                                  data={"name": "Jane",
                                        "email": "jane@jane.com"},
                                  follow_redirects=True)
        self.assertNotIn("<h2>Please RSVP</h2>", result.data)
        self.assertIn("<h2>Party Details</h2>", result.data)    

class PartyTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        #app.config['TESTING'] = True
        app.config.update(
            TESTING=True,
            SQLALCHEMY_TRACK_MODIFICATIONS=True
            )

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_games_logged_in(self):
        """Test to see if games list is showed when logged in."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['RSVP'] = True

        result = self.client.get("/games")
        self.assertIn("Monopoly", result.data)
        self.assertIn("The longest game ever with least action.", result.data)

    def test_games_logged_out(self):
        """Test to see if games list is NOT showed when logged out."""

        result = self.client.get("/games",
                                 follow_redirects=True)

        self.assertIn("Nice try! You need to be RSVP&#39;d first!", result.data)


if __name__ == "__main__":
    unittest.main()
