class BotContext:
    def __init__(self, database, helper_utils, client, tree):
        self.database = database
        self.helper_utils = helper_utils
        self.client = client
        self.tree = tree
