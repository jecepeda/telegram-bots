class Book:
    #TODO add parameters that allow saving the download link or the path of the book
    def __init__(self, id, title, description, image, isbn):
        self.id = id
        self.title = title
        self.description = description
        self.image = image
        self.isbn = isbn
        self.subtitle = ''

    def __str__(self):
        return "Title: {0}".format(self.title)
