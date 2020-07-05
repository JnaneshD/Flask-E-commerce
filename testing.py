from run import app
import logging
import requests

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['email'] = 'jnaneshdana@gmail.com'
        sess['_fresh'] = True
    resp = c.get('/some')
    assert resp



def test4():#display the products	
    response = app.test_client().get("/displayCategory",query_string=dict(categoryId="1"))
    assert response.status_code == 200
def test5():
    c = app.test_client()
    with c.session_transaction() as sess:
        sess['email'] = 'jnaneshdana@gmail.com'
        sess['_fresh'] = True
    response = c.get("/profile")#,query_string=dict(productId="9"))
    assert response.status_code == 200
def test6():
    response = app.test_client().get("/invoice")
    assert response.status_code == 200
def test7():
    response = app.test_client().get("/order",follow_redirects=True)
    assert response.status_code == 200
    assert "Print"
def test8():
    response = app.test_client().get("/profile")
    assert response.status_code == 302

def test9():
    response = app.test_client().get("/add")
    assert response.status_code == 200

