class TagMixin:
    @property
    def tag(self):
        if not getattr(self, "_TagMixin__tag", None):
            return None

        return self.__tag

    @tag.setter
    def tag(self, value):
        self.__tag = value
