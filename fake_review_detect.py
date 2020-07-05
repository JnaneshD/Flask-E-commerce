import sqlite3
import enchant
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
con = sqlite3.connect('database.db')
cur = con.cursor()
d = enchant.Dict("en_US")
cur.execute('SELECT * FROM reviews')
data = cur.fetchall()
stopwords.words('english')
ip=[]
for i in data:
  if(i[6] not in ip):
    ip.append(i[6])
z=[[[0,0] for _ in range(100)] for _ in range(len(ip))]
for i in data:
  b=(i[3]).split(" ")
  k=0
  for j in b:
    try:
      if(d.check(j)):
        k+=1
    except:
      pass
  fake=0
  if(k==0):
    fake=1
    reason="Contains no english words"
    cur.execute("UPDATE reviews set fake = ? , reason = ? where reviewid = ? ",(fake,reason,i[0],))
  else:
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(i[3]) 
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    filtered_sentence = [] 
    for w in word_tokens: 
      if w not in stop_words and w!=',' and w!=' ' and w!='.': 
        filtered_sentence.append(w) 
    if(len(filtered_sentence)==0):
      fake=1
      reason="Contains only stop words"
      cur.execute("UPDATE reviews set fake = ? , reason = ? where reviewid = ? ",(fake,reason,i[0],))
    else:
      p=0
      n=0 
      x=[]
      y=[]
      fake=0
      op1=open('negative-words.txt').read().split()
      op2=open('positive-words.txt').read().split()
      for m in op1:
        x.append(m)
        x.append(m.capitalize())
      for m in op2:
        y.append(m)
        y.append(m.capitalize())
      for w in word_tokens: 
          if w not in stop_words and w!=',' and w!=' ' and w!='.':
            if(w in x):
              #print(w,0)
              n+=1
            elif(w in y):
              #print(w,1)
              p+=1
      #print(n,p)
      if(p==0 and n>2):
        z[ip.index(i[6])][i[2]][0]+=1
      elif(n==0 and p>2):
        z[ip.index(i[6])][i[2]][1]+=1

for i in range(len(z)):
  for j in range(len(z[0])):
    if(max(z[i][j])>=3 and min(z[i][j])==0):
      fake=1
      reason="Multiple malicious reviews from same ip address"
      xx=j
      yy=ip[i]
      cur.execute("UPDATE reviews set fake = ? , reason = ? where productid = ? and ip = ?",(fake,reason,xx,yy,))
      con.commit()
