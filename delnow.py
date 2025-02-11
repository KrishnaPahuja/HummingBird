from main import db
from main.models import User, Post
from main import app

# # user1 = User(username='tony', email='stark@avengers.com', password='genius')
# # user2 = User(username='drax', email='ilovemantis@ego.com', password='ugly')

# # post1 = Post(title='black captian america', content='wakanda forever', user_id=1)
# # post2 = Post(title='magic book', content='warnings must be pre-written', user_id=1)

# # with app.app_context():

# #     db.create_all()

# #     db.session.add(user1)
# #     db.session.add(user2)
# #     db.session.add(post1)
# #     db.session.add(post2)
# #     db.session.commit()

# #     print(User.query.all())
# #     user = (User.query.first())
# #     print(user.id, user.posts)

# #     post = Post.query.first()
# #     print(post.author)

# #     falcon = User.query.filter_by(username='drax').first()
# #     print(falcon)

# #     db.drop_all()

with app.app_context():
    # db.create_all()
    print(User.query.all())
    print(Post.query.all())
    # db.drop_all()


# # with app.app_context():
# # # db.create_all()
# #     # User.query.all()
# #     db.create_all()
    

